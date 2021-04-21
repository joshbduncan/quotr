from flask_wtf import FlaskForm
from wtforms import TextAreaField, TextField, SelectField, SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    quote = TextAreaField('Quote', validators=[DataRequired()])
    author = TextField('Author', id='author', validators=[DataRequired()])
    category = SelectField('Category', id='category', coerce=int)
    submit = SubmitField('Submit')
