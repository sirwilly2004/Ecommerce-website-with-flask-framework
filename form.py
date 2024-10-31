from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditor, CKEditorField

# registration form for users
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('SIGN ME UP!')

# create post class (WTF)
class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    body = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('SUBMIT POST')

class Login(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('LOG ME IN')
