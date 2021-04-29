from flask_wtf import FlaskForm
from wtforms import TextAreaField, TextField, SelectField, SubmitField, StringField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    quote = TextAreaField('Quote', id='quote', validators=[DataRequired()])
    author = TextField('Author', id='author', validators=[DataRequired()])
    category = SelectField('Category', id='category', coerce=int)
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
