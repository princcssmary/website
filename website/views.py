from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, User
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/authenticator', methods=['GET', 'POST'])
@login_required
def authenticator():
    print(current_user.google_token)
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.id).first()
        if request.form.get('google_token'):
            print(request.form.get('google_token'), 'sdsdsd')
            user.google_authenticator = True
        else:
            print("Ggg")
            user.google_authenticator = False
        if request.form.get('email_token'):
            print(request.form.get('email_token'), 'sdsdsd')
            user.email_authenticator = True
        else:
            print("Ggg")
            user.email_authenticator = False
        db.session.commit()
    return render_template("authenticator.html", user=current_user, secret=current_user.google_token)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
