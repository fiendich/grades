from flask import Blueprint,render_template,request,flash,redirect,url_for
from .models import User
from werkzeug.security import generate_password_hash,check_password_hash
from . import db
from flask_login import login_user,login_required,logout_user,current_user

auth = Blueprint('auth',__name__)

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash('Logged in successfully',category='success')
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again',category='error')
        else:
            flash('Email does not exist.',category='error')

    return render_template("login.html",user=current_user)

@auth.route('/logout')
@login_required
def logout():
    login_user(current_user)
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Überprüfungen...
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email bereits registriert.', category='error')
            return redirect(url_for('auth.signup'))

        if password1 != password2:
            flash('Passwörter stimmen nicht überein.', category='error')
            return redirect(url_for('auth.signup'))

        new_user = User(email=email, firstName=first_name, password=generate_password_hash(password1, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        # 🔥 Reload user from DB to ensure it's not None
        user = User.query.filter_by(email=email).first()

        if user is not None:
            login_user(user, remember=True)
            flash('Konto erstellt!', category='success')
            return redirect(url_for('views.grades'))
        else:
            flash('Benutzer konnte nicht eingeloggt werden.', category='error')
            return redirect(url_for('auth.login'))

    return render_template("signup.html", user=current_user)
