
# Constructora ITC — Plataforma de Gestión de Proyectos

Este proyecto es una plataforma web desarrollada con Flask para la gestión de cotizaciones y proyectos de construcción e ingeniería. Permite a usuarios y administradores registrar, consultar y administrar solicitudes de servicios, así como gestionar archivos y usuarios.

## Características

- **Registro e inicio de sesión de usuarios** (con roles de usuario y administrador)
- **Panel de usuario:** Solicitud y gestión de cotizaciones/proyectos, subida y descarga de archivos técnicos y planos
- **Panel de administrador:** Gestión de usuarios y visualización de todos los proyectos
- **Edición y eliminación de proyectos y usuarios**
- **Carga y descarga segura de archivos**
- **Interfaz moderna y responsiva**

## Estructura del Proyecto

```
app.py
requirements.txt
static/
    css/style.css
    js/script.js
    img/
templates/
    base.html
    welcome.html
    login.html
    register.html
    user_dashboard.html
    admin_dashboard.html
    editar_usuario.html
    quienesomos.html
    servicios.html
    recuperar_contrasena.html
uploads/
```

## Instalación

1. **Clona el repositorio:**
   ```sh
   git clone <url-del-repo>
   cd ProyectoPracticas
   ```

2. **Crea un entorno virtual (opcional pero recomendado):**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Ejecuta la aplicación:**
   ```sh
   python app.py
   ```
   La aplicación estará disponible en [http://localhost:5050](http://localhost:5050).

## Usuario Administrador

Al iniciar la aplicación por primera vez, se crea automáticamente un usuario administrador:

- **Correo:** admin@constructora.com
- **Contraseña:** admin123

## Uso

- Los usuarios pueden registrarse, iniciar sesión y solicitar cotizaciones de servicios.
- Los administradores pueden gestionar usuarios y ver todos los proyectos desde el panel de administración.

## Personalización

- Modifica los estilos en `static/css/style.css`.
- Cambia las plantillas HTML en la carpeta `templates`.
- Los archivos subidos se almacenan en la carpeta `uploads`.

## Requisitos

- Python 3.7+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Werkzeug

## Licencia

Este proyecto es solo para fines educativos y de prácticas.

---

Desarrollado por Inaldo Turizo Correa — Construcción e Ingeniería responsable.