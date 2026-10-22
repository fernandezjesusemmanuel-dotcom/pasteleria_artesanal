import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Si no existe el usuario 'admin', lo crea automáticamente
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@pasteleria.com', 'Pasteleria2026!')
    print(">>> Superusuario 'admin' creado exitosamente.")
else:
    print(">>> El superusuario 'admin' ya existe.")