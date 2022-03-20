from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import pyotp
from .email_sender import EmailSender



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
                if current_user.google_authenticator:
                    return redirect(url_for("auth.login_2fa_form", email=email))

                if current_user.email_authenticator:
                    return redirect(url_for("auth.login_3fa_form", email=email))
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/login/2fa/", methods=['GET', 'POST'])
def login_2fa_form():
    email = request.args.get('email')
    valid = True
    if request.method == 'POST':
        # getting secret key used by user
        email = request.args.get('email')
        user = User.query.filter_by(email=email).first()
        google_token = user.google_token
        # getting OTP provided by user
        otp = int(request.form.get("otp"))
        print(google_token)
        # verifying submitted OTP with PyOTP

        if pyotp.TOTP(google_token).verify(otp):
            if current_user.email_authenticator:
                sender_mail = EmailSender([email], str(otp))
                sender_mail.start()
                sender_mail.send()
                return redirect(url_for("auth.login_3fa_form", email=email))
            else:
                return redirect(url_for('views.home'))

        flash("You have supplied an invalid 2FA token!", "danger")
        return redirect(url_for("auth.login_2fa_form", email=email))

    return render_template("login_2fa.html", email=email)

@auth.route("/login/3fa/", methods=['GET', 'POST'])
def login_3fa_form():
    email = request.args.get('email')
    valid = True
    if request.method == 'POST':
        # getting secret key used by user
        email = request.args.get('email')
        user = User.query.filter_by(email=email).first()
        google_token = current_user.google_token
        totp = pyotp.TOTP(google_token)
        otp = totp.now()
        # getting OTP provided by user
        otp = int(request.form.get("otp"))
        print(google_token)
        # verifying submitted OTP with PyOTP
        sender_mail = EmailSender([email], str(totp.now()))
        sender_mail.start()
        sender_mail.send()
        if pyotp.TOTP(google_token).verify(otp):
            return redirect(url_for('views.home'))

        flash("You have supplied an invalid 2FA token!", "danger")

        return redirect(url_for("auth.login_3fa_form", email=email))

    return render_template("login_3fa.html", email=email)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    secret = pyotp.random_base32()
    print(secret)
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
                            google_token=secret)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user, secret=secret)
