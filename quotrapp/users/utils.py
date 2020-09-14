import os
import secrets
from PIL import Image, ImageSequence
from flask import url_for
from flask_mail import Message
from quotrapp import mail
from flask import current_app


def delete_old_profile_picture(old_picture, root_path):
    # delete the previous profile pic to reduce unused files
    old_picture_path = os.path.join(
        root_path, 'static/profile_pics', old_picture)
    os.remove(old_picture_path)


def save_profile_picture(profile_picture, root_path):
    # generate a random value for profile pic filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(profile_picture.filename)

    picture_fname = random_hex + f_ext
    picture_path = os.path.join(
        root_path, 'static/profile_pics', picture_fname)

    # website image size
    output_size = (125, 125)

    # if uploaded pic is a gif, resize and re-animate
    if f_ext == '.gif':
        resize_gif(profile_picture, picture_path, output_size)
    else:
        img = Image.open(profile_picture)
        img.thumbnail(output_size)
        img.save(picture_path)

    return picture_fname


def resize_gif(picture, picture_path, output_size):
    img = Image.open(picture)
    frames = ImageSequence.Iterator(img)
    frames = thumbnails(frames, output_size)
    obj = next(frames)
    obj.info = img.info
    obj.save(picture_path, save_all=True, append_images=list(frames), loop=0)


def thumbnails(frames, output_size):
    for frame in frames:
        thumbnail = frame.copy()
        thumbnail.thumbnail(output_size, Image.ANTIALIAS)
        yield thumbnail


def send_reset_email(user):
    token = user.get_reset_token()
    sender = os.environ.get('MAIL_DEFAULT_SENDER')

    msg = Message('Password Reset Request',
                  sender=sender,
                  recipients=[user.email])

    msg.body = f'''To reset your password visit the following link:

{url_for('users_bp.reset_password', token=token, _external=True)}

If you did not make this request, simply ignore this email and no changes will be made.

- Quotr
'''

    mail.send(msg)
