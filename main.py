import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
import qrcode
from urllib.parse import urlparse

app = Flask(__name__)

# Configuraciones de Flask
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'clave-defecto-insegura')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortly.db'

# Limita tamaño a 2 MB por petición (protección básica)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

db = SQLAlchemy(app)

# El resto de tu código sigue igual...


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    user = db.relationship('User', backref=db.backref('links', lazy=True))


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choices(characters, k=length))
        if not Link.query.filter_by(short_code=short_code).first():
            return short_code


def valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


def generate_qr_code(url, code):
    qr_folder = os.path.join(app.root_path, 'static', 'qrcodes')
    os.makedirs(qr_folder, exist_ok=True)
    filename = f'qr_{code}.png'
    qr_path = os.path.join(qr_folder, filename)
    img = qrcode.make(url)
    img.save(qr_path)
    return filename


login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def home():
    new_url = None
    link = None
    if request.method == "POST":
        original_url = request.form.get("url")

        if not valid_url(original_url):
            flash("Por favor introduce una URL válida (ejemplo: https://tudominio.com).")
            return redirect(url_for("home"))

        short_code = generate_short_code()
        new_url = url_for('redirect_short',
                          short_code=short_code, _external=True)
        user_id = current_user.id if current_user.is_authenticated else None
        link = Link(original_url=original_url,
                    short_code=short_code, user_id=user_id)
        db.session.add(link)
        db.session.commit()

        qr_filename = generate_qr_code(new_url, link.id)
        link.qr_filename = qr_filename
        db.session.commit()

    links = None
    if current_user.is_authenticated:
        links = Link.query.filter_by(user_id=current_user.id).all()

    return render_template("form.html", new_url=new_url, link=link, links=links)


@app.route('/<short_code>')
def redirect_short(short_code):
    link = Link.query.filter_by(short_code=short_code).first_or_404()
    return redirect(link.original_url)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("El nombre de usuario ya existe. Escoge otro.")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Usuario registrado con éxito. Por favor, inicia sesión.")
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Inicio de sesión exitoso.")
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos.")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    db.create_all()
