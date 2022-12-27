from flask import (
    make_response,
    request,
    Flask
)

from decouple import config
from auth import auth


app = Flask(__name__)


@app.route('/', methods=['POST'])
@auth.login_required
def send_bot():
    data_messagem = request.get_json()

    return make_response({'envio': 'sucesso'}, 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config('PORT'))
