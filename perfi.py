from flask import Blueprint, render_template, request, redirect, url_for, flash, session

# Crear el blueprint
profile_bp = Blueprint('profile', __name__, template_folder='../templates')

# Ruta para ver el perfil
@profile_bp.route('/profile')
def view_profile():
    if 'user' not in session:
        flash('Necesitas iniciar sesión para ver tu perfil.')
        return redirect(url_for('auth.login'))

    user = session['user']
    return render_template('profile.html', user=user)

# Ruta para editar el perfil
@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        flash('Necesitas iniciar sesión para editar tu perfil.')
        return redirect(url_for('auth.login'))

    user = session['user']

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_bio = request.form.get('bio')

        # Aquí iría la lógica para actualizar en la base de datos.
        user['username'] = new_username
        user['bio'] = new_bio
        session['user'] = user  # actualizar en sesión

        flash('Perfil actualizado exitosamente.')
        return redirect(url_for('profile.view_profile'))

    return render_template('edit_profile.html', user=user)
