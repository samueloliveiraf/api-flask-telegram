from flask import (
    make_response,
    request,
    Flask
)

from decouple import config
from auth import auth
from message import (
    messagem_erro,
    messagem_sucesso
)

import requests, random

from time import sleep

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver


app = Flask(__name__)


def get_cookie_value(cookie_list, li_at, session_id):
    try:
        list_cookie = list()
        for cookie in cookie_list:
            print(f" - {cookie['name']}: {cookie['value']}")
            if cookie['name'] == li_at:
                list_cookie.append(cookie['value'])
            elif cookie['name'] == session_id:
                list_cookie.append(cookie['value'].replace('"', ''))

            if len(list_cookie) == 2:
                return list_cookie
            else:
                continue
    except Exception as e:
        print(f"Error in get_cookie_value: {e}")
        return None


@app.route('/', methods=['POST'])
@auth.login_required
def send_bot():
    data_messagem = request.get_json()
    try:
        if data_messagem.get('erro'):
            mensagem = messagem_erro(data_messagem['erro'])
        else:
            mensagem = messagem_sucesso(data_messagem['sucesso'])

        bot_token = config('KEY_BOT')
        chat_id = config('CHAT_ID')
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        params = {'chat_id': chat_id, 'text': f'{mensagem}'}
        requests.get(url, params=params)

        return make_response({'envio': 'sucesso'}, 200)

    except Exception as e:
        error = str(e)
        return make_response({'error': f'Error {error}'}, 400)


@app.route('/auth-linkedin/', methods=['POST'])
@auth.login_required
def auth_linkedin():
    data_request = request.get_json()

    firefox_options = Options()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                 "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    firefox_options.add_argument(f"--user-agent={user_agent}")
    firefox_options.add_argument("--lang=pt-BR")
    firefox_options.add_argument("--headless")
    firefox_options.add_argument('--window-size=1920,1080')
    firefox_options.add_argument("--no-sandbox")

    driver = webdriver.Firefox(options=firefox_options)

    try:
        driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(
            data_request['email']
        )
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(
            data_request['password']
        )

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))).click()

        sleep(2)

        cookie_list = driver.get_cookies()
        cookie_val = get_cookie_value(cookie_list, 'li_at', 'JSESSIONID')
        cookie_val = {'li_at': cookie_val[0], 'JSESSIONID': cookie_val[1]}
        if cookie_val:
            return make_response(cookie_val), 200

        else:
            response = f'Login linkedin invalid'
            return make_response({'validation_errors': response}), 401

    except Exception as e:
        errors = str(e)
        response = f'Error executing Selenium code: {errors}'

        return make_response({'validation_errors': response}, 400)

    finally:
        driver.quit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config('PORT'))
