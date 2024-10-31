from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask, render_template, request, jsonify, redirect,url_for, flash
from datetime import datetime
import smtplib
import time
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditor, CKEditorField
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
import bleach
from form import RegistrationForm, CreatePostForm,Login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from flask import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = '225635GDUETHIAHSGDY7333'
ckeditor = CKEditor(app)
Bootstrap(app)

# Load environment variables
load_dotenv()



# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)

# Models for Posts and Users
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    author = relationship("Users", back_populates="posts")   
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    subtitle = db.Column(db.String(200), nullable=False)
    img_url = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Post {self.title}>'

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # define a one to many relationship between the code 
    posts = db.relationship('Post', back_populates='author')

    def __repr__(self):
        return f'<User {self.full_name}>'

# Create tables
with app.app_context():
    db.create_all()

# Login Manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Email configuration
MY_EMAIL = os.getenv('MY_EMAIL')
MY_PASSWORD = os.getenv('MY_PASSWORD')
RECIPIENT_EMAIL = MY_EMAIL

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)        
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/insert_data')
def sample_data():
    database_post = Post.query.all()
    # Add some sample data (this should have real data)
    sample_posts = [
            {
                "title": "The Future of Remote Work",
                "body": "Remote work has transformed the workplace landscape. Companies are now adopting hybrid models that combine in-office and remote work. This shift requires new management strategies and tools to maintain productivity and team cohesion.",
                "author": "Sarah Johnson",
                "subtitle": "Navigating the new normal of work-life balance.",
                "date": "2023-09-25"
            }
             ]
 
    with app.app_context():  
        for post_data in sample_posts:  
        # Convert date string to datetime object  
            post_data['date'] = datetime.strptime(post_data['date'], '%Y-%m-%d')  
            post = Post(**post_data)  # Unpack the dictionary into the Post constructor  
            # Check if there is an existing post with the same title  
            check = Post.query.filter_by(title=post.title).first()  
            if not check:  
                db.session.add(post) 
        db.session.commit()

# Function to send emails
def send_email(name, email, phone, message):
    subject = "New User for the Coding Class Whitelist"
    body = f"""
    Name: {name}
    Email: {email}
    Phone: {phone}
    Message: {message}
    """
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(MY_EMAIL, MY_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Routes
@app.route("/")
def home_page():
    posts = Post.query.all()
    return render_template("index.html", year=datetime.now().year, all_post=posts)

@app.route('/about')
def about():
    return render_template('about.html', year=datetime.now().year)

@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = Post.query.get(post_id)
    if requested_post is None:
        return "Post not found", 404
    formatted_date = requested_post.date.strftime('%B %d, %Y')
    return render_template("post.html", post=requested_post, year=datetime.now().year, formatted_date=formatted_date)

@app.route('/contact', methods=["POST", "GET"])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email_address = request.form.get('email_address')
        phone_number = request.form.get('phone_number')
        messages = request.form.get('messages')

        send_email(name, email_address, phone_number, messages)
        return render_template("contact.html", msg_sent=True, year=datetime.now().year)
    return render_template("contact.html", msg_sent=False, year=datetime.now().year)

@app.route('/new_post', methods=["GET", "POST"])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            subtitle=form.subtitle.data,
            author_id=current_user.id,
            img_url=form.img_url.data,
            body=form.body.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home_page'))
    return render_template('new-post.html', form=form, year=datetime.now().year)

@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    requested_post = Post.query.get(post_id)
    if requested_post is None:
        return "Post not found", 404
    edit_form = CreatePostForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        img_url=requested_post.img_url,
        body=requested_post.body
    )
    if edit_form.validate_on_submit():
        requested_post.title = edit_form.title.data
        requested_post.subtitle = edit_form.subtitle.data
        requested_post.img_url = edit_form.img_url.data
        requested_post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template('new-post.html', form=edit_form, post=requested_post, year=datetime.now().year)

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    post_to_delete = Post.query.get(post_id)
    if post_to_delete is None:
        return "Post not found", 404
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home_page'))

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = Users(
            full_name=form.full_name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=12)
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("home_page")) 
    return render_template("register.html", form=form, year=datetime.now().year)

if __name__ == '__main__':
    app.run(debug=True)
