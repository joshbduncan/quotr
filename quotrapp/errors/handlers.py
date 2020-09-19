from flask import Blueprint, render_template
from quotrapp.errors.utils import send_error_email


errors_bp = Blueprint('errors_bp', __name__)


@errors_bp.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@errors_bp.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@errors_bp.app_errorhandler(500)
def error_500(error):
    print('********************************* ERROR **************************************')
    print('********************************* ERROR **************************************')
    print(error)
    print('********************************* ERROR **************************************')
    print('********************************* ERROR **************************************')
    send_error_email(error)
    return render_template('errors/500.html'), 500
