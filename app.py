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

import requests


app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config('PORT'))
