import requests
from requests.exceptions import ReadTimeout, ConnectionError
import telegram
import time
import os
import logging

TOKEN_BOT = os.environ.get('TOKEN_BOT')
TOKEN_API = os.environ.get('TOKEN_API')
CHAT_ID = os.environ.get('CHAT_ID')

data_headers = {
    'Authorization': 'Token ' + TOKEN_API
}

BASE_URL = 'https://dvmn.org'
BASE_URL_API = BASE_URL + '/api/'

long_polling = BASE_URL_API + 'long_polling/'

bot = telegram.Bot(token=TOKEN_BOT)


def main():
    request_params = {}
    logger = logging.getLogger('NOTICE')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(filename='app.log', format='[%(asctime)s] : %(name)s : %(levelname)s : [%(message)s]')
    logger.addHandler(LoggerHandler(bot=bot))
    logger.info('Бот успешно запущен')

    while True:
        try:
            response = requests.get(long_polling, headers=data_headers, params=request_params)
            response.raise_for_status()
            dict_response = response.json()

            status = dict_response['status']
            timestamp = get_timestamp(status=status, dict_response=dict_response)

            request_params = {'timestamp': timestamp}

            answer = dict_response['new_attempts'][0]

            msg = get_msg(dict_response=answer)

            bot.send_message(chat_id=CHAT_ID, text=msg)
            time.sleep(1)

        except ReadTimeout:
            logger.warning('превышено время ожидания')
        except ConnectionError:
            logger.warning('нет соединения с интернетом')
        except KeyError:
            continue
        except Exception:
            logger.exception(msg='Бот упал с ошибкой:', exc_info=True)
            time.sleep(10)


def get_timestamp(status, dict_response):
    if status == 'found':
        timestamp = dict_response['last_attempt_timestamp']
    elif status == 'timeout':
        timestamp = dict_response['timestamp_to_request']
    return timestamp


def get_msg(dict_response):
    is_verified = not dict_response['is_negative']
    lesson_title = dict_response['lesson_title']
    lesson_url = BASE_URL + dict_response['lesson_url']
    msg = f'У Вас проверили работу "{lesson_title}" {lesson_url} '
    if is_verified:
        msg += 'Преподавателю всё понравилось, можно приступать к следущему уроку'
    else:
        msg += f'К сожалению в работе нашлись ошибки'
    return msg


class LoggerHandler(logging.Handler):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        print(log_entry)
        self.bot.send_message(chat_id=CHAT_ID, text=log_entry)


if __name__ == '__main__':
    main()
