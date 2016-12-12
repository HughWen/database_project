from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix='/topics/auth')

from . import views
