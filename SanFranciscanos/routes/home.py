from flask import Blueprint, render_template

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    return render_template('pagina-inicio.html')

@bp.route('/login')
def login():
    return render_template('log-in.html')
