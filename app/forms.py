from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class DishForm(FlaskForm):
    rating = SelectField('Rating', coerce=int, choices=[0, 1, 2, 3, 4, 5], validators=[DataRequired()])
    comments = TextAreaField('Comments (optional)', validators=[DataRequired()])
    submit = SubmitField('Add Dish Review')


class RestaurantForm(FlaskForm):
    rating = SelectField('Rating', coerce=int, choices=[0, 1, 2, 3, 4, 5], validators=[DataRequired()])
    comments = TextAreaField('Comments (optional)', validators=[DataRequired()])
    submit = SubmitField('Add Restaurant Review')
