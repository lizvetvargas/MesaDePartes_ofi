MESA DE PARTES DIGITAL — JARDÍN SANTA RITA DE CASIA

INSTALACIÓN EN WINDOWS (PowerShell):
1) Abre la terminal en la carpeta del proyecto.
2) python -m venv .venv
3) .\.venv\Scripts\Activate.ps1
4) python -m pip install -r requirements.txt
5) Copia .env.example a .env y cambia SECRET_KEY.
6) python -m flask --app app crear-tablas
7) python -m flask --app app crear-direccion
8) python -m flask --app app run --debug
9) Abre http://127.0.0.1:5000

PRUEBAS:
python -m pytest -v

GOOGLE:
Configura un cliente OAuth de aplicación web en Google Cloud Console.
URI de retorno local: http://127.0.0.1:5000/auth/google/callback
Copia Client ID y Client Secret en .env y reinicia la aplicación.
El usuario debe existir previamente y tener rol asignado; Google no concede privilegios automáticamente.

IMPORTANTE:
Esta es una base de desarrollo para continuar construyendo. No cargues datos reales de menores todavía.
La vinculación de padres requiere verificación institucional antes de usarla en producción.
Antes de publicar se deben completar validación real de archivos, verificación de parentesco,
auditoría, recuperación de contraseñas, protección contra intentos repetidos, HTTPS y respaldos.
No compartas el archivo .env ni subas secretos a GitHub.
