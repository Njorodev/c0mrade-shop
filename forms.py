from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, FloatField, PasswordField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = TextAreaField('Description')
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    images = MultipleFileField('Product Images')  # <-- add this line
    submit = SubmitField('Add Product')
class SearchForm(FlaskForm):
    search_query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
