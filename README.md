# 🍰 Pastelería Artesanal - Plataforma Web de Gestión y Catálogo Online

Sistema web integral desarrollado con **Django** orientado a la gestión comercial, control de producción, administración de recetas/ingredientes y catálogo digital de pedidos para un emprendimiento de pastelería artesanal.

---

## 🚀 Despliegue en Producción
* **URL Pública:** [https://pasteleria-artesanal.onrender.com](https://pasteleria-artesanal.onrender.com)
* **Plataforma de Hosting:** Render (Web Service con servidor WSGI Gunicorn).
* **Gestión de Estáticos:** WhiteNoise con compresión y cacheado `CompressedManifestStaticFilesStorage`.

---
## 📦 Estrategia de Inicialización y Persistencia en la Nube (Seed Data)

El servicio en producción corre bajo un contenedor con sistema de archivos efímero en Render. Con el objetivo de garantizar una experiencia de evaluación y auditoría ininterrumpida (sin depender de bases de datos externas de vencimiento temporal como PostgreSQL Free Tier de 30 días), se implementó una estrategia automatizada de **Database Seeding**:

* **Aprovisionamiento Automático (`crear_admin.py`):** Inicializa de forma idempotente las credenciales del superusuario del panel de administración sin exponer contraseñas en el código fuente.
* **Carga de Datos de Demostración (`poblar_datos.py`):** Inyecta automáticamente categorías de repostería, productos de catálogo activos con stock y fichas técnicas de materias primas/insumos con umbrales de alerta.
* **Pipeline de Construcción Automatizado:** Durante cada ciclo de despliegue (`Build Command`), Render ejecuta de manera encadenada la recolección de estáticos, la aplicación de migraciones y la carga de datos base:
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python crear_admin.py && python poblar_datos.py
---

## 🔒 Arquitectura de Seguridad y Hardening en Producción
Para garantizar la integridad de los datos, la privacidad de los pedidos y la mitigación de vulnerabilidades comunes (OWASP Top 10), el sistema implementa las siguientes medidas validadas mediante la suite interna de auditoría de Django (`check --deploy`):

1. **Aislamiento de Secretos y Configuración de Entorno:**
   * Uso de `python-dotenv` para segregar credenciales críticas (`SECRET_KEY`, credenciales de correo y administración) fuera del control de versiones (`.gitignore`).
2. **Defensa contra Host Header Poisoning:**
   * Restricción estricta de `ALLOWED_HOSTS` a subdominios autorizados de Render (`.onrender.com`) y entornos de loopback locales, descartando comodines permissivos.
3. **Protección Criptográfica de Transporte (HTTPS / HSTS):**
   * Redirección forzada de tráfico inseguro hacia HTTPS (`SECURE_SSL_REDIRECT = True`).
   * Activación de **HTTP Strict Transport Security (HSTS)** por 31536000 segundos (1 año) con directivas `includeSubDomains` y `preload`.
4. **Blindaje de Sesiones y Cookies:**
   * Marcado obligatorio de cookies de sesión y CSRF como seguras (`SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`).
   * Prevención de accesos indebidos por scripts maliciosos con `HttpOnly` activo (`SESSION_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_HTTPONLY = True`).
5. **Mitigación de Ataques XSS y Clickjacking:**
   * Cabeceras de seguridad activadas: `SECURE_BROWSER_XSS_FILTER = True`, `SECURE_CONTENT_TYPE_NOSNIFF = True` y `X_FRAME_OPTIONS = 'DENY'`.
6. **Sanitización y Validación de Archivos Adjuntos:**
   * El modelo de comprobantes de pago (`comprobante_sena`) implementa `FileExtensionValidator` restringiendo formatos exclusivamente a `jpg`, `jpeg`, `png` y `pdf`.
   * Validación a nivel de modelo para impedir la subida de archivos superiores a 5 MB, previniendo denegación de servicio por agotamiento de almacenamiento.
7. **Automatización Segura de Administración en la Nube:**
   * Implementación de un script desacoplado (`crear_admin.py`) para inicializar el superusuario en la base de datos de producción mediante variables de entorno inyectadas, sin exponer credenciales en el código fuente.

---

## 🛠️ Tecnologías Utilizadas
* **Backend:** Python 3.12 / Django 6.x
* **Base de Datos:** SQLite / Motor relacional compatible con Django ORM
* **Servidor WSGI:** Gunicorn
* **Almacenamiento Estático:** WhiteNoise
* **Control de Versiones y Despliegue:** Git / GitHub / Render CD Pipeline

---

## 💻 Ejecución en Entorno Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/fernandezjesusemmanuel-dotcom/pasteleria_artesanal.git](https://github.com/fernandezjesusemmanuel-dotcom/pasteleria_artesanal.git)
   cd pasteleria_artesanal