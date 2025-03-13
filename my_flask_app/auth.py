from flask import Blueprint,render_template,redirect,url_for,request,flash
from werkzeug.security import generate_password_hash,check_password_hash
from .models import User
from . import db

auth = Blueprint('auth',__name__)

# Wtch tutorial 6 for more nice management of database

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup',methods = ['POST'])
def signup_post():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    # if len(password) < 6:                   #Add more security checks later      
    #     flash('Password must be at least 6 characters long.', 'danger')
    #     return redirect(url_for('auth.signup'))

    # #debug
    # print("Signup: ",name,email,password)
    user = User.query.filter_by(email=email).first()
    if user:
        flash('User already exists. Please log in.', 'warning')
        return redirect(url_for('auth.login'))
    
    new_user = User(
        name = name,
        email = email,
        password = generate_password_hash(password,method='pbkdf2:sha256') #Why did we choose this?
    )

    db.session.add(new_user)
    try:
        db.session.commit()
        flash('Signup Successful!','success')
    except Exception as e:
        print("Error during commit:", e)
        db.session.rollback()
        return "An error occurred while signing up.", 500
    
    return redirect(url_for('auth.login'))


@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login',methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('User with provided E-mail does not exist please signup','error')
        return redirect(url_for('auth.signup'))
    if not check_password_hash(user.password,password):
        flash('Password is incorrect, please try again!','error')
        return redirect(url_for('auth.login'))
    
    return 'Login Successful'

