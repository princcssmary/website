from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import pyotp

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                #return redirect(url_for('views.home'))
                return redirect(url_for("auth.login_2fa_form"))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/login/2fa/", methods=['GET', 'POST'])
def login_2fa_form():
    secret = pyotp.random_base32()
    if request.method == 'POST':
        # getting secret key used by user
        secret = request.form.get("secret")
        # getting OTP provided by user
        otp = int(request.form.get("otp"))

        # verifying submitted OTP with PyOTP
        if pyotp.TOTP(secret).verify(otp):
            # inform users if OTP is valid
            flash("The TOTP 2FA token is valid", "success")
            return redirect(url_for("auth.login_2fa_form"))
        else:
            # inform users if OTP is invalid
            flash("You have supplied an invalid 2FA token!", "danger")
            return redirect(url_for("auth.login_2fa_form"))

    return render_template("login_2fa.html", secret=secret)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email,
                            first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'),
                            google_token=pyotp.random_base32())
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
