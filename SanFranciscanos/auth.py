from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from blogr import db

bp = Blueprint('auth',__name__, url_prefix ='/auth')

@bp.route('/register',methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User(username,email,generate_password_hash(password))

        error = None

        user_email = User.query.filter_by(email = email).first()
        if user_email == None:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            error = f"El email '{email}' ya esta registrado"
            flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods = ('GET','POST'))
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        error = None
        user = User.query.filter_by(email = email).first()

        if user == None or not check_password_hash(user.password,password):
            error = 'Correo o contraseña incorrecta'
            flash(error)
        
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('post.posts'))

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.index'))

import functools

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

from werkzeug.utils import secure_filename

@bp.route('/perfil/<int:id>', methods = ('GET','POST'))
@login_required
def perfil(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        password = request.form.get("password")

        error = None
        if len(password) != 0:
            user.password = generate_password_hash(password)
        elif len(password) > 0 and len(password) <6:
            error = "La contraseña debe tener más de 5 caracteres"


        if request.files['photo']:
            photo = request.files['photo']
            photo.save(f'blogr/static/media/{secure_filename(photo.filename)}')
            user.photo = f"media/{secure_filename(photo.filename)}"
        
        if error is not None:
            flash(error)
        else:
            db.session.commit()
            return redirect(url_for('home.index'))
        
        flash(error)

    return render_template('auth/profile.html', user = user)

