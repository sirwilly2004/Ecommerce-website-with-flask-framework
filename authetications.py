from flask import Flask, render_template, request, jsonify, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user



app = Flask(__name__)
app.config['SECRET_KEY'] = '2256your secretl;3'


# CONNECT TO DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)

class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Post {self.full_name}>'
    

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        new_user = Users(
            full_name=request.form.get('full_name'),
            email=request.form.get('email'),
            password=request.form.get('password')
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("register.html")
