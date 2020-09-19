from flask_mail import Message
from quotrapp import mail
from flask import current_app


def send_error_email(error):
    admin_addr = current_app.config['MAIL_DEFAULT_SENDER']

    msg = Message('Internal Server Error',
                  sender=admin_addr,
                  recipients=[admin_addr])

    msg.body = f'{error}'

    mail.send(msg)
