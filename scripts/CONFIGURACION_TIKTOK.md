# 🔧 Guía de Configuración de TikTok API

Esta guía te ayudará a configurar correctamente el Client Key de TikTok para que el sistema funcione.

## ⚠️ Error: "client_key" no configurado

Si ves el error: **"We couldn't log in with TikTok. This may be due to specific app settings. client_key"**, significa que necesitas configurar tu Client Key de TikTok.

## 📋 Pasos para Configurar TikTok API

### Paso 1: Crear una Cuenta de Desarrollador

1. Ve a [TikTok for Developers](https://developers.tiktok.com/)
2. Inicia sesión con tu cuenta de TikTok (debe ser la cuenta **@kassy_138**)
3. Si no tienes cuenta de desarrollador, créala

### Paso 2: Crear una Aplicación

1. En el portal de desarrolladores, ve a **"My Apps"** o **"Mis Aplicaciones"**
2. Haz clic en **"Create App"** o **"Crear Aplicación"**
3. Completa el formulario:
   - **App Name**: Nombre de tu aplicación (ej: "TikTok Scheduler")
   - **App Category**: Selecciona una categoría apropiada
   - **Description**: Descripción de tu aplicación
4. Acepta los términos y condiciones
5. Haz clic en **"Submit"** o **"Enviar"**

### Paso 3: Obtener Credenciales

1. Una vez creada la aplicación, ve a la sección **"Basic Information"** o **"Información Básica"**
2. Encontrarás:
   - **Client Key** (también llamado App ID)
   - **Client Secret** (secreto de la aplicación)
3. **Copia estos valores** - los necesitarás más adelante

### Paso 4: Configurar Redirect URI

1. En la configuración de tu aplicación, busca la sección **"Redirect URI"** o **"URI de Redirección"**
2. Agrega la siguiente URI:
   ```
   http://localhost:8000/
   ```
   O si estás usando otro puerto:
   ```
   http://localhost:8000/callback
   ```
3. **IMPORTANTE**: El Redirect URI debe coincidir EXACTAMENTE con el que uses en el código
4. Guarda los cambios

### Paso 5: Configurar Permisos (Scopes)

1. En la configuración de tu aplicación, busca **"Permissions"** o **"Permisos"**
2. Habilita los siguientes permisos:
   - ✅ `user.info.basic` - Información básica del usuario
   - ✅ `video.upload` - Subir videos
   - ✅ `video.publish` - Publicar videos

### Paso 6: Configurar el Client Key en el Código

#### Opción A: Editar el archivo HTML (Recomendado para pruebas)

1. Abre el archivo `tiktok_scheduler.html`
2. Busca la línea 360:
   ```javascript
   const TIKTOK_CLIENT_KEY = 'TU_CLIENT_KEY_AQUI';
   ```
3. Reemplaza `'TU_CLIENT_KEY_AQUI'` con tu Client Key real:
   ```javascript
   const TIKTOK_CLIENT_KEY = 'tu_client_key_aqui';
   ```
4. Guarda el archivo

#### Opción B: Crear archivo de configuración (Recomendado para producción)

1. Copia el archivo `tiktok_config.example.py` a `tiktok_config.py`:
   ```bash
   cp tiktok_config.example.py tiktok_config.py
   ```

2. Edita `tiktok_config.py` y completa:
   ```python
   TIKTOK_CLIENT_KEY = 'tu_client_key_real'
   TIKTOK_CLIENT_SECRET = 'tu_client_secret_real'
   TIKTOK_REDIRECT_URI = 'http://localhost:8000/'
   ```

3. **NO** compartas este archivo - contiene credenciales sensibles

### Paso 7: Verificar la Configuración

1. Inicia el servidor:
   ```bash
   python tiktok_scheduler_backend.py
   ```

2. Abre el navegador en `http://localhost:8000`

3. Verifica que no aparezca el mensaje de advertencia sobre el Client Key

4. Haz clic en **"Autorizar con TikTok"**

5. Deberías ser redirigido a TikTok para autorizar

## 🔍 Solución de Problemas

### Error: "client_key" no válido

**Causas posibles:**
- El Client Key no está configurado
- El Client Key tiene espacios o caracteres extra
- El Client Key es incorrecto

**Solución:**
1. Verifica que el Client Key esté correctamente copiado (sin espacios)
2. Asegúrate de que esté entre comillas: `'tu_client_key'`
3. Verifica en el portal de TikTok que la aplicación esté activa

### Error: "redirect_uri_mismatch"

**Causa:** El Redirect URI no coincide con el configurado en TikTok

**Solución:**
1. Verifica en TikTok Developer Portal que el Redirect URI sea exactamente:
   - `http://localhost:8000/` o
   - `http://localhost:8000/callback`
2. Asegúrate de que no haya espacios o caracteres extra
3. El Redirect URI debe coincidir EXACTAMENTE (incluyendo http/https, puerto, y ruta)

### Error: "invalid_scope"

**Causa:** Los permisos (scopes) no están habilitados en la aplicación

**Solución:**
1. Ve a la configuración de tu aplicación en TikTok
2. Habilita los siguientes permisos:
   - `user.info.basic`
   - `video.upload`
   - `video.publish`
3. Guarda los cambios y espera unos minutos para que se propaguen

### Error: "app_not_approved"

**Causa:** La aplicación no ha sido aprobada por TikTok

**Solución:**
1. Algunas aplicaciones requieren aprobación de TikTok
2. Completa todos los campos requeridos en la configuración
3. Espera la aprobación (puede tardar varios días)
4. Para desarrollo, algunas funciones pueden estar limitadas

### La aplicación no aparece en TikTok Developer Portal

**Solución:**
1. Asegúrate de estar iniciado sesión con la cuenta correcta
2. Verifica que hayas completado el registro como desarrollador
3. Intenta crear una nueva aplicación

## 📝 Checklist de Configuración

Antes de intentar autorizar, verifica:

- [ ] Tienes una cuenta en TikTok for Developers
- [ ] Has creado una aplicación en el portal
- [ ] Has copiado el Client Key correctamente
- [ ] Has configurado el Redirect URI en TikTok
- [ ] Has habilitado los permisos necesarios
- [ ] Has actualizado el Client Key en `tiktok_scheduler.html` o `tiktok_config.py`
- [ ] El servidor está corriendo en el puerto correcto
- [ ] Estás usando la cuenta **@kassy_138** para autorizar

## 🔐 Seguridad

- **NUNCA** compartas tu Client Secret públicamente
- **NO** subas `tiktok_config.py` a repositorios públicos
- Mantén tus credenciales seguras
- Si crees que tus credenciales están comprometidas, regenera el Client Secret en TikTok

## 📚 Recursos Adicionales

- [TikTok for Developers](https://developers.tiktok.com/)
- [Documentación de OAuth](https://developers.tiktok.com/doc/login-kit-web/)
- [Guía de Configuración de Aplicaciones](https://developers.tiktok.com/doc/getting-started-create-an-app/)

## 💡 Notas Importantes

1. **Cuenta Objetivo**: Asegúrate de autorizar con la cuenta **@kassy_138**
2. **Redirect URI**: Debe coincidir EXACTAMENTE en TikTok y en el código
3. **Permisos**: Todos los permisos necesarios deben estar habilitados
4. **Aprobación**: Algunas funciones pueden requerir aprobación de TikTok

Si después de seguir estos pasos aún tienes problemas, verifica los logs del servidor para más detalles del error.








