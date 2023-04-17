from wtforms import Form, StringField, TextAreaField, \
    PasswordField, SubmitField, validators, ValidationError, \
    RadioField, DateField

from flask_wtf import FlaskForm
from src.models import UserModel
from wtforms.validators import DataRequired, URL, Email,EqualTo,Regexp,Length


# User/Customer Registration form
class UserRegisterForm(FlaskForm):
    name = StringField('Name: ', validators=[DataRequired()])
    username = StringField('Username: ', [validators.DataRequired()])
    email = StringField('Email: ', validators=[validators.Email(), validators.DataRequired()])
    birthday = DateField('Birth Date', format='%Y-%m-%d')
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')],validators=[validators.DataRequired()])

    password = PasswordField('Password : ', validators=[DataRequired(),
                                                            EqualTo('confirm',
                                                                    message=' Both password must match! '),
                                                            Length(min=6, max=12,
                                                                   message="Please enter a password between 6 and 12 characters long."),
                                                            Regexp(
                                                                r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^\w\d\s]).{6,12}$',
                                                                message="Please enter a password with at least one uppercase letter, one lowercase letter, one number, and one special character.")
                                                            ],
                             id="password")
    confirm = PasswordField('Repeat Password : ', validators=[DataRequired()], id="conpassword")

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if UserModel.query.filter_by(username=username.data).first():
            raise ValidationError("This username is already in use!")

    def validate_email(self, email):
        if UserModel.query.filter_by(email=email.data).first():
            raise ValidationError("This email address is already in use!")


class CustomerProfileForm(FlaskForm):
    country = StringField('Country: ', [validators.DataRequired()])
    city = StringField('City: ', [validators.DataRequired()])
    contact = StringField('Contact: ', [validators.DataRequired()])
    address = StringField('Address: ', [validators.DataRequired()])
    zipcode = StringField('Zip code: ', [validators.DataRequired()])
    submit = SubmitField('Submit')


class UserLoginFrom(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')

