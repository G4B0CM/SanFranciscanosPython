from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import functools
from SanFranciscanos import users

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        error = None
        if users.find_user_by_email(email):
            error = f"El email '{email}' ya está registrado"
        else:
            users.create_user(username, email, password)
            return redirect(url_for('auth.login'))

        if error:
            flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users.find_user_by_email(email)
        error = None

        if not user or not users.verify_password(user, password):
            error = 'Correo o contraseña incorrecta'
        else:
            session.clear()
            session['user_id'] = str(user['_id'])
            return redirect(url_for('home.index'))

        if error:
            flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = users.get_user_by_id(user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/perfil/<id>', methods=['GET', 'POST'])
@login_required
def perfil(id):
    user = users.get_user_by_id(id)
    if not user:
        flash("Usuario no encontrado.")
        return redirect(url_for('home.index'))

    if request.method == 'POST':
        new_username = request.form.get('username')
        password = request.form.get("password")
        updates = {'username': new_username}
        error = None

        if password:
            if len(password) < 6:
                error = "La contraseña debe tener más de 5 caracteres"
            else:
                updates['password'] = generate_password_hash(password)

        if 'photo' in request.files and request.files['photo'].filename != '':
            photo = request.files['photo']
            filename = secure_filename(photo.filename)
            photo.save(f'static/media/{filename}')
            updates['photo'] = f"media/{filename}"

        if error:
            flash(error)
        else:
            users.update_user(id, updates)
            flash("Perfil actualizado correctamente.")
            return redirect(url_for('home.index'))

    return render_template('auth/profile.html', user=user)
