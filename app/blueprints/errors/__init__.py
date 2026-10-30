from flask import Blueprint

errors_bp = Blueprint('errors', __name__, template_folder='../../templates/errors')

from app.blueprints.errors import handlers  # noqa: E402, F401

