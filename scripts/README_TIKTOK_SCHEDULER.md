# TikTok Scheduler - Programador Automático de Posts

Sistema completo para autenticarse con TikTok y programar automáticamente posts desde una carpeta de imágenes.

**🎯 Cuenta Objetivo: @kassy_138** - Todos los posts se publicarán en esta cuenta específica.

## 🚀 Características

- ✅ Autenticación OAuth con TikTok
- ✅ Interfaz web moderna y fácil de usar
- ✅ Programación automática de posts (4 por día por defecto)
- ✅ Horarios aleatorios configurables
- ✅ Soporte para captions desde archivos JSON de Instagram
- ✅ Vista previa del calendario
- ✅ Estado del sistema en tiempo real

## 📋 Requisitos Previos

1. **Cuenta de Desarrollador de TikTok**
   - Registrarse en [TikTok for Developers](https://developers.tiktok.com/)
   - Crear una aplicación
   - Obtener `Client Key` y `Client Secret`
   - Configurar Redirect URI: `http://localhost:8000/callback`

2. **Python 3.8+**
3. **Carpeta con contenido**: `scripts/instagram_downloads/69caylin`

## 🔧 Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements_tiktok_scheduler.txt
```

2. **Configurar credenciales de TikTok:**
   
   ⚠️ **IMPORTANTE**: Si ves el error "client_key", sigue la guía completa en `CONFIGURACION_TIKTOK.md`
   
   **Opción A: Editar HTML (Recomendado para pruebas)**
   
   Abre `tiktok_scheduler.html` línea 360 y reemplaza:
   ```javascript
   const TIKTOK_CLIENT_KEY = 'TU_CLIENT_KEY_AQUI';
   ```
   Con tu Client Key real de TikTok.
   
   **Opción B: Archivo de configuración (Recomendado para producción)**
   
   Copia `tiktok_config.example.py` a `tiktok_config.py` y completa:
   ```python
   TIKTOK_CLIENT_KEY = 'tu_client_key_real'
   TIKTOK_CLIENT_SECRET = 'tu_client_secret_real'
   ```
   
   O configura variables de entorno:
   ```bash
   export TIKTOK_CLIENT_KEY="tu_client_key"
   export TIKTOK_CLIENT_SECRET="tu_client_secret"
   ```
   
   📖 **Ver guía completa**: `CONFIGURACION_TIKTOK.md`

## 🎯 Uso

1. **Iniciar el servidor backend:**
```bash
cd scripts
python tiktok_scheduler_backend.py
```

2. **Abrir el navegador:**
   - Navega a `http://localhost:8000`
   - Verás la interfaz de programación

3. **Autenticarse con TikTok:**
   - Haz clic en "Autorizar con TikTok"
   - **IMPORTANTE:** Inicia sesión con la cuenta **@kassy_138**
   - Autoriza la aplicación
   - El sistema validará que sea la cuenta correcta
   - Serás redirigido de vuelta

4. **Configurar programación:**
   - Posts por día: 4 (por defecto)
   - Fecha de inicio: Selecciona la fecha
   - Horarios aleatorios: Activado por defecto
   - Rango de horarios: 09:00-22:00 (por defecto)

5. **Generar calendario:**
   - Haz clic en "Generar Calendario"
   - Revisa la vista previa
   - Haz clic en "Guardar y Activar Programación"

6. **Iniciar programador:**
   - Haz clic en "Iniciar Programador"
   - El sistema publicará automáticamente según el calendario

## 📁 Estructura de Archivos

```
scripts/
├── tiktok_scheduler.html          # Interfaz web
├── tiktok_scheduler_backend.py    # Servidor backend
├── requirements_tiktok_scheduler.txt
├── tiktok_schedule.json           # Calendario guardado (generado)
├── tiktok_tokens.json             # Tokens OAuth (generado)
├── instagram_downloads/
│   └── 69caylin/                  # Carpeta con imágenes
│       ├── *.jpg                  # Imágenes
│       └── *.json                 # Metadata con captions
```

## ⚙️ Configuración Avanzada

### Cambiar número de posts por día
En la interfaz web, modifica el campo "Posts por día"

### Cambiar rango de horarios
Formato: `HH:MM-HH:MM` (ejemplo: `09:00-22:00`)

### Horarios fijos vs aleatorios
- **Aleatorios**: Los horarios se distribuyen aleatoriamente en el rango
- **Fijos**: Los horarios se distribuyen uniformemente

## 🔒 Seguridad

- Los tokens se guardan localmente en `tiktok_tokens.json`
- **NO** compartas este archivo
- Los tokens expiran y se refrescan automáticamente
- El sistema valida que la cuenta autorizada sea **@kassy_138** antes de publicar
- No se permitirá publicar en cuentas diferentes a la objetivo

## 📝 Notas Importantes

1. **TikTok API y Videos:**
   - TikTok principalmente acepta videos
   - Las imágenes necesitan convertirse a video
   - El sistema actualmente loguea las publicaciones
   - Para producción, necesitarás implementar conversión imagen→video

2. **Límites de la API:**
   - TikTok tiene límites de rate limiting
   - Respeta los términos de servicio
   - No publiques contenido que viole las políticas

3. **Captions:**
   - Se extraen automáticamente de los archivos JSON de Instagram
   - Se limitan a 150 caracteres (límite de TikTok)
   - Si no hay JSON, se usa un caption por defecto

## 🐛 Solución de Problemas

### Error: "client_key" o "No se pudo obtener token"
- **Este es el error más común** - Verifica la guía completa en `CONFIGURACION_TIKTOK.md`
- Verifica que tu Client Key esté configurado en `tiktok_scheduler.html` línea 360
- Asegúrate de que el Redirect URI coincida EXACTAMENTE con el configurado en TikTok
- Verifica que los permisos (scopes) estén habilitados en TikTok Developer Portal

### Error: "Token inválido"
- Los tokens expiran después de cierto tiempo
- El sistema intenta refrescarlos automáticamente
- Si falla, necesitarás re-autorizar

### Error: "Cuenta incorrecta"
- Asegúrate de autorizar con la cuenta **@kassy_138**
- El sistema no permitirá publicar en otras cuentas
- Si ves este error, cierra sesión y autoriza nuevamente con la cuenta correcta

### No se encuentran archivos de contenido
- Verifica que la carpeta `instagram_downloads/69caylin` exista
- Asegúrate de que contenga archivos `.jpg` o `.png`

## 📚 Recursos

- [TikTok for Developers](https://developers.tiktok.com/)
- [TikTok API Documentation](https://developers.tiktok.com/doc/)
- [OAuth 2.0 Guide](https://developers.tiktok.com/doc/login-kit-web/)

## ⚠️ Disclaimer

Este sistema es para uso educativo y personal. Asegúrate de cumplir con:
- Términos de servicio de TikTok
- Políticas de contenido
- Leyes locales sobre automatización

