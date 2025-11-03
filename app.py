from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
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
    proyectos = db.relationship('Proyecto', backref='usuario', lazy=True)


# --- MODELO DE PROYECTO ---
class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_empresa = db.Column(db.String(100), nullable=False)
    nit_empresa = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    servicio = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    presupuesto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    archivo_tecnico = db.Column(db.String(200))  # Ruta del archivo subido
    plano = db.Column(db.String(200))  # Ruta del plano subido
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- FUNCIÓN PARA CREAR BD Y ADMIN ---
def inicializar_bd():
    with app.app_context():
        db.create_all()
        # Crear carpeta uploads si no existe
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
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
            print("Usuario administrador creado (admin@constructora.com / admin123)")
        else:
            print("Usuario administrador ya existe.")

# --- RUTAS ---
@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/quienes-somos')
def quienes_somos():
    return render_template('quienesomos.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

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
    # Obtener proyectos del usuario para mostrar
    proyectos = Proyecto.query.filter_by(user_id=current_user.id).all()
    return render_template('user_dashboard.html', proyectos=proyectos)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/proyecto/<int:proyecto_id>/eliminar', methods=['POST'])
@login_required
def eliminar_proyecto(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)

    # Verificar que el proyecto pertenece al usuario actual
    if proyecto.user_id != current_user.id:
        flash('No tienes permiso para eliminar este proyecto', 'error')
        return redirect(url_for('user_dashboard'))

    # Eliminar archivos si existen
    if proyecto.archivo_tecnico:
        archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], proyecto.archivo_tecnico)
        if os.path.exists(archivo_path):
            os.remove(archivo_path)

    if proyecto.plano:
        plano_path = os.path.join(app.config['UPLOAD_FOLDER'], proyecto.plano)
        if os.path.exists(plano_path):
            os.remove(plano_path)

    # Eliminar de la base de datos
    db.session.delete(proyecto)
    db.session.commit()

    flash('Proyecto eliminado correctamente', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/proyecto/<int:proyecto_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_proyecto(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)

    # Verificar que el proyecto pertenece al usuario actual
    if proyecto.user_id != current_user.id:
        flash('No tienes permiso para editar este proyecto', 'error')
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        proyecto.nombre_empresa = request.form['nombre_empresa']
        proyecto.nit_empresa = request.form['nit_empresa']
        proyecto.telefono = request.form['telefono']
        proyecto.direccion = request.form['direccion']
        proyecto.servicio = request.form['servicio']
        proyecto.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        proyecto.presupuesto = float(request.form['presupuesto'])
        proyecto.descripcion = request.form['descripcion']

        # Manejo de archivos - solo actualizar si se suben nuevos
        if 'archivo_tecnico' in request.files and request.files['archivo_tecnico'].filename != '':
            # Eliminar archivo anterior si existe
            if proyecto.archivo_tecnico:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], proyecto.archivo_tecnico)
                if os.path.exists(old_path):
                    os.remove(old_path)

            archivo_tecnico = request.files['archivo_tecnico']
            archivo_tecnico_filename = secure_filename(archivo_tecnico.filename)
            archivo_tecnico.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo_tecnico_filename))
            proyecto.archivo_tecnico = archivo_tecnico_filename

        if 'plano' in request.files and request.files['plano'].filename != '':
            # Eliminar archivo anterior si existe
            if proyecto.plano:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], proyecto.plano)
                if os.path.exists(old_path):
                    os.remove(old_path)

            plano = request.files['plano']
            plano_filename = secure_filename(plano.filename)
            plano.save(os.path.join(app.config['UPLOAD_FOLDER'], plano_filename))
            proyecto.plano = plano_filename

        db.session.commit()
        flash('Proyecto actualizado correctamente', 'success')
        return redirect(url_for('user_dashboard'))

    # Para GET, mostrar el formulario de edición
    proyectos = Proyecto.query.filter_by(user_id=current_user.id).all()
    return render_template('user_dashboard.html', proyectos=proyectos, proyecto_editar=proyecto)

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    # Verificar que el archivo pertenece a un proyecto del usuario actual
    proyecto = Proyecto.query.filter(
        (Proyecto.archivo_tecnico == filename) | (Proyecto.plano == filename),
        Proyecto.user_id == current_user.id
    ).first()

    if not proyecto:
        flash('Archivo no encontrado o no tienes permiso para descargarlo', 'error')
        return redirect(url_for('user_dashboard'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        flash('Archivo no encontrado en el servidor', 'error')
        return redirect(url_for('user_dashboard'))

    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/user_dashboard', methods=['GET', 'POST'])
@login_required
def cotizacion():
    if request.method == 'POST':
        nombre_empresa = request.form['nombre_empresa']
        nit_empresa = request.form['nit_empresa']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        servicio = request.form['servicio']
        fecha = request.form['fecha']
        presupuesto = request.form['presupuesto']
        descripcion = request.form['descripcion']

        # Manejo de archivos
        archivo_tecnico_filename = None
        plano_filename = None

        if 'archivo_tecnico' in request.files:
            archivo_tecnico = request.files['archivo_tecnico']
            if archivo_tecnico.filename != '':
                archivo_tecnico_filename = secure_filename(archivo_tecnico.filename)
                archivo_tecnico.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo_tecnico_filename))

        if 'plano' in request.files:
            plano = request.files['plano']
            if plano.filename != '':
                plano_filename = secure_filename(plano.filename)
                plano.save(os.path.join(app.config['UPLOAD_FOLDER'], plano_filename))

        # Guardar en base de datos
        nuevo_proyecto = Proyecto(
            nombre_empresa=nombre_empresa,
            nit_empresa=nit_empresa,
            telefono=telefono,
            direccion=direccion,
            servicio=servicio,
            fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
            presupuesto=float(presupuesto),
            descripcion=descripcion,
            archivo_tecnico=archivo_tecnico_filename,
            plano=plano_filename,
            user_id=current_user.id
        )
        db.session.add(nuevo_proyecto)
        db.session.commit()

        flash('Cotización registrada con éxito', 'success')
        return redirect(url_for('user_dashboard'))

    # Obtener proyectos del usuario para mostrar
    proyectos = Proyecto.query.filter_by(user_id=current_user.id).all()
    return render_template('user_dashboard.html', proyectos=proyectos)


#-- INICIAR LA APLICACIÓN ---
if __name__ == '__main__':
    inicializar_bd()
    app.run(debug=True, port=5050)