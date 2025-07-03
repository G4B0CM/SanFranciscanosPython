from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from SanFranciscanos import users
import functools
import os

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        error = None
        if users.find_user_by_email(email):
            error = f"El email '{email}' ya está registrado."
        elif not username or not email or not password:
            error = "Todos los campos son obligatorios."
        elif len(password) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."
        else:
            users.create_user(username, email, password)
            flash("Usuario registrado correctamente.", "success")
            return redirect(url_for('auth.login'))

        if error:
            flash(error, "danger")

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users.find_user_by_email(email)
        error = None

        if not user or not users.verify_password(user, password):
            error = "Correo o contraseña incorrectos."
        else:
            session.clear()
            session['user_id'] = str(user['_id'])
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('home.index'))

        if error:
            flash(error, "danger")

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
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('home.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Debes iniciar sesión para acceder a esta sección.", "warning")
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/perfil/<id>', methods=['GET', 'POST'])
@login_required
def perfil(id):
    user = users.get_user_by_id(id)
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('home.index'))

    if request.method == 'POST':
        new_username = request.form.get('username')
        password = request.form.get("password")
        updates = {'username': new_username}
        error = None

        # Validar y actualizar contraseña
        if password:
            if len(password) < 6:
                error = "La contraseña debe tener al menos 6 caracteres."
            else:
                updates['password'] = generate_password_hash(password)

        # Guardar foto si se sube
        if 'photo' in request.files and request.files['photo'].filename != '':
            photo = request.files['photo']
            filename = secure_filename(photo.filename)
            ruta_media = os.path.join(current_app.root_path, 'static', 'media')
            os.makedirs(ruta_media, exist_ok=True)
            photo.save(os.path.join(ruta_media, filename))
            updates['photo'] = f"media/{filename}"

        if error:
            flash(error, "danger")
        else:
            users.update_user(id, updates)
            flash("Perfil actualizado correctamente.", "success")
            return redirect(url_for('home.index'))

    return render_template('auth/profile.html', user=user)
