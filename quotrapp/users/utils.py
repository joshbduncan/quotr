import os
import secrets
from PIL import Image, ImageSequence
from flask import url_for
from flask_mail import Message
from quotrapp import mail
from flask import current_app
import boto3


s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
s3_bucket = 'quotr-static'


def s3_file_upload(picture_fname, picture_path):
    with open(picture_path, "rb") as f:
        s3_client.upload_fileobj(f, s3_bucket, picture_fname, ExtraArgs={
                                 'ACL': 'public-read'})


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

    s3_file_upload(picture_fname, picture_path)

    return picture_fname


def delete_old_profile_picture(old_picture, root_path):
    # delete the previous profile pic to reduce unused files
    # old_picture_path = os.path.join(
    #     root_path, 'static/profile_pics', old_picture)
    # if check_old_profile_picture(old_picture, root_path):
    #     os.remove(old_picture_path)
    file = s3.Object(s3_bucket, old_picture)
    file.delete()


def check_old_profile_picture(old_picture, root_path):
    # old_picture_path = os.path.join(
    #     root_path, 'static/profile_pics', old_picture)
    # if os.path.exists(old_picture_path):
    #     return True
    # else:
    #     return False
    files = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=old_picture)
    if files['KeyCount'] > 0:
        return True
    else:
        return False


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
    sender = current_app.config['MAIL_DEFAULT_SENDER']

    msg = Message('Password Reset Request',
                  sender=sender,
                  recipients=[user.email])

    msg.body = f'''To reset your password visit the following link:

{url_for('users_bp.reset_password', token=token, _external=True)}

If you did not make this request, simply ignore this email and no changes will be made.

- Quotr
'''

    mail.send(msg)
