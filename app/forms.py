from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=30, message="Username must be between 3 and 30 characters.")
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message="Email is required."),
        Email(message="Please provide a valid email address."),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=6, message="Password must be at least 6 characters.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.strip()).first()
        if user:
            raise ValidationError("This username is already taken. Please choose another.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError("An account with this email already exists.")


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message="Email is required."),
        Email(message="Please provide a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required.")
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class PostForm(FlaskForm):
    title = StringField('Post Title', validators=[
        DataRequired(message="Title is required."),
        Length(min=3, max=150, message="Title must be between 3 and 150 characters.")
    ])
    category_id = SelectField('Category', coerce=int, validators=[
        DataRequired(message="Please select a category.")
    ])
    content = TextAreaField('Post Content (Markdown supported)', validators=[
        DataRequired(message="Content cannot be empty."),
        Length(min=10, message="Content must be at least 10 characters long.")
    ])
    submit = SubmitField('Publish Post')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[
        DataRequired(message="Comment content cannot be empty."),
        Length(min=1, max=2000, message="Comment must be between 1 and 2000 characters.")
    ])
    submit = SubmitField('Post Comment')


class SearchForm(FlaskForm):
    q = StringField('Search posts...', validators=[Length(max=100)])
    category = SelectField('Category', choices=[('', 'All Categories')], default='')
    sort = SelectField('Sort By', choices=[('newest', 'Newest First'), ('oldest', 'Oldest First')], default='newest')
