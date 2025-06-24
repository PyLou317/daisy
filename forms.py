from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, DecimalField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from wtforms.widgets import TextArea
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class OnboardingForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])

class ContractorForm(FlaskForm):
    talent_name = StringField('Talent Name', validators=[DataRequired()])
    job_title = StringField('Job Title', validators=[Optional()])
    candidate_status = SelectField('Status', choices=[
        ('Current', 'Current'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
        ('Terminated', 'Terminated')
    ], default='Current')
    talent_start_date = DateField('Start Date', validators=[Optional()])
    talent_end_date = DateField('End Date', validators=[Optional()])
    mobile = StringField('Mobile Phone', validators=[Optional()])
    talent_id = StringField('Talent ID', validators=[Optional()])
    recruiter = StringField('Recruiter', validators=[Optional()])
    account_manager = StringField('Account Manager', validators=[Optional()])
    account_name = StringField('Account Name', validators=[Optional()])
    spread_amount = DecimalField('Spread Amount ($)', validators=[
        Optional(),
        NumberRange(min=0, message="Spread amount must be positive")
    ], places=2)

class UploadForm(FlaskForm):
    file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    description = TextAreaField('Description (Optional)', validators=[Optional()])
