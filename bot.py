import requests
from requests.exceptions import ReadTimeout, ConnectionError
import telegram
import time
import os

TOKEN_BOT = os.environ.get('TOKEN_BOT')
TOKEN_API = os.environ.get('TOKEN_API')
CHAT_ID = os.environ.get('CHAT_ID')


def main():
    bot = telegram.Bot(token=TOKEN_BOT)

    data_headers = {
        'Authorization': 'Token ' + TOKEN_API
    }

    request_params = {}

    base_url = 'https://dvmn.org'
    base_url_api = base_url + '/api/'
    long_polling = base_url_api + 'long_polling/'

    while True:
        try:
            response = requests.get(long_polling, headers=data_headers, params=request_params)

            response.raise_for_status()
            dict_response = response.json()

            status = dict_response['status']
            if status == 'found':
                timestamp = dict_response['last_attempt_timestamp']
            elif status == 'timeout':
                timestamp = dict_response['timestamp_to_request']

            request_params = {'timestamp': timestamp}

            answer = dict_response['new_attempts'][0]
            is_verified = not answer['is_negative']
            lesson_title = answer['lesson_title']
            lesson_url = base_url + answer['lesson_url']

            msg = f'У Вас проверили работу "{lesson_title}" {lesson_url} '
            if is_verified:
                msg += 'Преподавателю всё понравилось, можно приступать к следущему уроку'
            else:
                msg += f'К сожалению в работе нашлись ошибки'

            bot.send_message(chat_id=CHAT_ID, text=msg)
            time.sleep(1)

        except ReadTimeout:
            print('превышено время ожидания')
        except ConnectionError:
            print('нет соединения с интернетом')
        except KeyError:
            continue


if __name__ == '__main__':
    main()
