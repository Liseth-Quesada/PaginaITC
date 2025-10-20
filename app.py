from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# --- MODELO DE USUARIO ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='usuario')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- FUNCIÓN PARA CREAR BD Y ADMIN ---
def inicializar_bd():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(email='admin@constructora.com').first()
        if not admin:
            admin = User(
                nombre='Administrador',
                email='admin@constructora.com',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                rol='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado (admin@constructora.com / admin123)")
        else:
            print("ℹ️ Usuario administrador ya existe.")


# --- RUTAS ---
@app.route('/')
def index():
    return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Credenciales incorrectas', 'error')
            return redirect(url_for('login'))

        login_user(user)

        # Redirige según el rol
        if user.rol == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        if User.query.filter_by(email=email).first():
            flash('El correo ya está registrado', 'error')
            return redirect(url_for('register'))

        nuevo_usuario = User(nombre=nombre, email=email, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Registro exitoso, ahora puede iniciar sesión', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.rol != 'admin':
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('user_dashboard'))

    usuarios = User.query.all()
    return render_template('admin_dashboard.html', usuarios=usuarios)


@app.route('/user')
@login_required
def user_dashboard():
    if current_user.rol == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('user_dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    inicializar_bd()
    app.run(debug=True)
