from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from decouple import config

auth = HTTPBasicAuth()


users = {
    config('USER_NAME'): generate_password_hash(config('USER_PASSWD'))
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
