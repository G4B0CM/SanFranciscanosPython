from flask import Blueprint, render_template, request



bp = Blueprint('home',__name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/login')
def revista():
    return render_template('log-in.html')