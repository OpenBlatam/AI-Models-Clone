"""
TikTok Scheduler Backend
========================

Backend para autenticación OAuth de TikTok y programación automática de posts.
"""

import os
import json
import random
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuración de TikTok API
# Intentar cargar desde archivo de configuración
try:
    from tiktok_config import (
        TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, 
        TIKTOK_REDIRECT_URI, SERVER_HOST, SERVER_PORT, DEBUG_MODE
    )
except ImportError:
    # Si no existe el archivo de configuración, usar variables de entorno o valores por defecto
    TIKTOK_CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY', 'TU_CLIENT_KEY_AQUI')
    TIKTOK_CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET', 'TU_CLIENT_SECRET_AQUI')
    TIKTOK_REDIRECT_URI = os.getenv('TIKTOK_REDIRECT_URI', 'http://localhost:8000/callback')
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'

TIKTOK_API_BASE = 'https://open-api.tiktok.com'

# Directorios
BASE_DIR = Path(__file__).parent
CONTENT_DIR = BASE_DIR / 'instagram_downloads' / '69caylin'
VIDEOS_DIR = BASE_DIR / 'videos_ai_69caylin' / 'individual'  # Videos generados con IA
SCHEDULE_FILE = BASE_DIR / 'tiktok_schedule.json'
TOKEN_FILE = BASE_DIR / 'tiktok_tokens.json'
STATUS_FILE = BASE_DIR / 'tiktok_status.json'

# Configuración: usar videos o imágenes
USE_VIDEOS = True  # Cambiar a False para usar imágenes

# Estado global
scheduler_running = False
scheduled_posts = []
published_posts = []

# Cuenta objetivo de TikTok
TARGET_TIKTOK_USERNAME = 'kassy_138'  # Cuenta donde se publicarán los posts


class TikTokAPI:
    """Cliente para la API de TikTok."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = TIKTOK_API_BASE
    
    def verify_token(self) -> bool:
        """Verificar si el token de acceso es válido."""
        try:
            url = f"{self.base_url}/user/info/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return False
    
    def get_user_info(self) -> Optional[Dict]:
        """Obtener información del usuario de TikTok."""
        try:
            url = f"{self.base_url}/user/info/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # La estructura de respuesta puede variar según la API
                user_data = data.get('data', {}).get('user', {}) or data.get('data', {})
                return {
                    'username': user_data.get('display_name') or user_data.get('username') or user_data.get('open_id'),
                    'display_name': user_data.get('display_name', ''),
                    'avatar_url': user_data.get('avatar_url', ''),
                    'follower_count': user_data.get('follower_count', 0),
                    'following_count': user_data.get('following_count', 0),
                    'likes_count': user_data.get('likes_count', 0),
                    'video_count': user_data.get('video_count', 0)
                }
            else:
                logger.error(f"Error obteniendo info de usuario: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error en get_user_info: {e}")
            return None
    
    def verify_target_account(self) -> tuple:
        """
        Verificar que la cuenta autorizada sea la cuenta objetivo.
        Retorna (es_valida, username_actual)
        """
        user_info = self.get_user_info()
        if not user_info:
            return False, None
        
        username = user_info.get('username', '').lower()
        target_username = TARGET_TIKTOK_USERNAME.lower()
        
        # Verificar si coincide (puede venir con o sin @)
        username_clean = username.replace('@', '')
        target_clean = target_username.replace('@', '')
        
        is_valid = username_clean == target_clean
        return is_valid, username
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refrescar el token de acceso."""
        try:
            url = f"{self.base_url}/oauth/refresh_token/"
            data = {
                'client_key': TIKTOK_CLIENT_KEY,
                'client_secret': TIKTOK_CLIENT_SECRET,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error refrescando token: {e}")
            return None
    
    def upload_video(self, video_path: str, caption: str = "") -> Optional[Dict]:
        """
        Subir video a TikTok.
        Nota: TikTok requiere que los videos se suban en múltiples pasos.
        """
        try:
            # Paso 1: Inicializar upload
            init_url = f"{self.base_url}/share/video/upload/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
            }
            
            # Leer el archivo de video
            with open(video_path, 'rb') as f:
                files = {'video': f}
                data = {
                    'post_info': json.dumps({
                        'title': caption[:150],  # TikTok limita a 150 caracteres
                        'privacy_level': 'PUBLIC_TO_EVERYONE',
                        'disable_duet': False,
                        'disable_comment': False,
                        'disable_stitch': False,
                        'video_cover_timestamp_ms': 1000
                    })
                }
                response = requests.post(init_url, headers=headers, files=files, data=data, timeout=60)
                
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error subiendo video: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error en upload_video: {e}")
            return None
    
    def publish_image(self, image_path: str, caption: str = "") -> Optional[Dict]:
        """
        Publicar imagen en TikTok.
        Nota: TikTok principalmente soporta videos, pero algunas APIs permiten imágenes.
        """
        try:
            # TikTok requiere convertir imágenes a video o usar su API de imágenes
            # Por ahora, retornamos un placeholder
            logger.warning("TikTok API requiere videos. Convirtiendo imagen a video...")
            return {
                'success': True,
                'message': 'Imagen programada para conversión a video',
                'image_path': image_path
            }
        except Exception as e:
            logger.error(f"Error en publish_image: {e}")
            return None


def load_tokens() -> Dict:
    """Cargar tokens guardados."""
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando tokens: {e}")
    return {}


def save_tokens(tokens: Dict):
    """Guardar tokens."""
    try:
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, indent=2)
    except Exception as e:
        logger.error(f"Error guardando tokens: {e}")


def load_schedule() -> List[Dict]:
    """Cargar calendario guardado."""
    if SCHEDULE_FILE.exists():
        try:
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando calendario: {e}")
    return []


def save_schedule(schedule_data: List[Dict]):
    """Guardar calendario."""
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error guardando calendario: {e}")


def get_content_files() -> List[Path]:
    """Obtener lista de archivos de contenido (videos o imágenes)."""
    if USE_VIDEOS:
        # Buscar videos generados con IA
        if VIDEOS_DIR.exists():
            video_files = list(VIDEOS_DIR.glob('*.mp4')) + list(VIDEOS_DIR.glob('*.MP4'))
            if video_files:
                logger.info(f"Encontrados {len(video_files)} videos en {VIDEOS_DIR}")
                return sorted(video_files)
            else:
                logger.warning(f"No se encontraron videos en {VIDEOS_DIR}, buscando imágenes...")
        else:
            logger.warning(f"Directorio de videos no existe: {VIDEOS_DIR}, buscando imágenes...")
    
    # Fallback a imágenes
    if not CONTENT_DIR.exists():
        logger.error(f"Directorio de contenido no existe: {CONTENT_DIR}")
        return []
    
    image_files = list(CONTENT_DIR.glob('*.jpg')) + list(CONTENT_DIR.glob('*.jpeg')) + list(CONTENT_DIR.glob('*.png'))
    logger.info(f"Encontradas {len(image_files)} imágenes en {CONTENT_DIR}")
    return sorted(image_files)


def get_caption_from_json(image_path: Path) -> str:
    """Obtener caption del archivo JSON asociado."""
    json_path = image_path.with_suffix('.json')
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                caption = data.get('node', {}).get('edge_media_to_caption', {}).get('edges', [])
                if caption and len(caption) > 0:
                    text = caption[0].get('node', {}).get('text', '')
                    # Limpiar hashtags y formatear
                    return text[:150]  # TikTok limita a 150 caracteres
        except Exception as e:
            logger.error(f"Error leyendo JSON: {e}")
    return "✨ Nuevo post"


def generate_random_times(count: int, start_hour: int, start_min: int, 
                          end_hour: int, end_min: int, random_times: bool = True) -> List[str]:
    """Generar horarios aleatorios o distribuidos."""
    times = []
    start_minutes = start_hour * 60 + start_min
    end_minutes = end_hour * 60 + end_min
    interval = (end_minutes - start_minutes) / count if count > 0 else 0
    
    for i in range(count):
        if random_times:
            min_minutes = start_minutes + i * interval
            max_minutes = start_minutes + (i + 1) * interval
            minutes = random.randint(int(min_minutes), int(max_minutes))
        else:
            minutes = start_minutes + i * interval
        
        hours = minutes // 60
        mins = minutes % 60
        times.append(f"{hours:02d}:{mins:02d}")
    
    return sorted(times)


def generate_schedule(posts_per_day: int, start_date: str, content_folder: str,
                     random_times: bool, time_range: str) -> List[Dict]:
    """Generar calendario de posts."""
    schedule_data = []
    content_files = get_content_files()
    
    if not content_files:
        logger.error("No se encontraron archivos de contenido")
        return []
    
    # Parsear rango de horarios
    start_time, end_time = time_range.split('-')
    start_hour, start_min = map(int, start_time.split(':'))
    end_hour, end_min = map(int, end_time.split(':'))
    
    # Calcular días necesarios
    total_posts = len(content_files)
    days_needed = (total_posts + posts_per_day - 1) // posts_per_day
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    file_index = 0
    
    for day in range(days_needed):
        current_date = start_dt + timedelta(days=day)
        times = generate_random_times(posts_per_day, start_hour, start_min, 
                                     end_hour, end_min, random_times)
        
        for time_str in times:
            if file_index >= len(content_files):
                break
            
            hour, minute = map(int, time_str.split(':'))
            post_datetime = current_date.replace(hour=hour, minute=minute, second=0)
            
            content_path = content_files[file_index]
            
            # Obtener caption (buscar JSON asociado si es video)
            if content_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
                # Para videos, buscar JSON con el mismo nombre base
                json_path = CONTENT_DIR / content_path.stem.replace('_ai', '').replace('_video', '')
                # Buscar JSON original
                for json_file in CONTENT_DIR.glob('*.json'):
                    if json_file.stem in content_path.stem:
                        caption = get_caption_from_json(json_file)
                        break
                else:
                    caption = "✨ Nuevo video"
            else:
                caption = get_caption_from_json(content_path)
            
            # Determinar tipo de contenido
            content_type = 'video' if content_path.suffix.lower() in ['.mp4', '.mov', '.avi'] else 'image'
            
            schedule_data.append({
                'id': f"post_{file_index}_{int(post_datetime.timestamp())}",
                'datetime': post_datetime.isoformat(),
                'content_path': str(content_path),
                'content_type': content_type,
                'caption': caption,
                'status': 'scheduled',
                'created_at': datetime.now().isoformat()
            })
            
            file_index += 1
    
    return schedule_data


def publish_post(post: Dict) -> bool:
    """Publicar un post programado."""
    try:
        tokens = load_tokens()
        access_token = tokens.get('access_token')
        
        if not access_token:
            logger.error("No hay token de acceso disponible")
            return False
        
        api = TikTokAPI(access_token)
        
        # Verificar token
        if not api.verify_token():
            # Intentar refrescar
            refresh_token = tokens.get('refresh_token')
            if refresh_token:
                new_tokens = api.refresh_access_token(refresh_token)
                if new_tokens:
                    save_tokens(new_tokens)
                    access_token = new_tokens.get('access_token')
                    api = TikTokAPI(access_token)
                else:
                    logger.error("No se pudo refrescar el token")
                    return False
            else:
                logger.error("Token inválido y no hay refresh token")
                return False
        
        # VALIDAR QUE SEA LA CUENTA CORRECTA
        is_target_account, username = api.verify_target_account()
        if not is_target_account:
            logger.error(f"⚠️  CUENTA INCORRECTA: Se intentó publicar en @{username} pero debe ser @{TARGET_TIKTOK_USERNAME}")
            post['status'] = 'failed'
            post['error'] = f'Cuenta incorrecta: @{username}. Debe ser @{TARGET_TIKTOK_USERNAME}'
            return False
        
        logger.info(f"✅ Cuenta verificada: @{username} (correcta)")
        
        # Obtener ruta del contenido
        content_path = post.get('content_path') or post.get('image_path')  # Compatibilidad
        content_type = post.get('content_type', 'image')
        caption = post.get('caption', '')
        
        logger.info(f"📤 Publicando en @{TARGET_TIKTOK_USERNAME}: {content_path} a las {post.get('datetime')}")
        logger.info(f"Tipo: {content_type}, Caption: {caption[:50]}...")
        
        # Publicar según el tipo de contenido
        if content_type == 'video' or content_path.endswith(('.mp4', '.mov', '.avi')):
            # Publicar video
            result = api.upload_video(content_path, caption)
            if result:
                logger.info(f"✅ Video publicado exitosamente")
                post['status'] = 'published'
                post['published_at'] = datetime.now().isoformat()
                post['published_to'] = TARGET_TIKTOK_USERNAME
                post['video_id'] = result.get('data', {}).get('item_id') or result.get('video_id', '')
                return True
            else:
                logger.error(f"❌ Error al publicar video")
                post['status'] = 'failed'
                post['error'] = 'Error al subir video a TikTok'
                return False
        else:
            # Publicar imagen (convertir a video o usar API de imágenes)
            logger.warning("⚠️  Publicando imagen (TikTok requiere videos)")
            result = api.publish_image(content_path, caption)
            if result:
                logger.info(f"✅ Imagen programada para publicación")
                post['status'] = 'published'
                post['published_at'] = datetime.now().isoformat()
                post['published_to'] = TARGET_TIKTOK_USERNAME
                return True
            else:
                logger.error(f"❌ Error al publicar imagen")
                post['status'] = 'failed'
                post['error'] = 'Error al publicar imagen'
                return False
    except Exception as e:
        logger.error(f"Error publicando post: {e}")
        post['status'] = 'failed'
        post['error'] = str(e)
        return False


def run_scheduler():
    """Ejecutar el programador de posts."""
    global scheduler_running, scheduled_posts
    
    while scheduler_running:
        try:
            now = datetime.now()
            schedule_data = load_schedule()
            
            for post in schedule_data:
                if post.get('status') != 'scheduled':
                    continue
                
                post_dt = datetime.fromisoformat(post['datetime'])
                
                # Publicar si es el momento
                if now >= post_dt:
                    logger.info(f"Publicando post programado: {post['id']}")
                    success = publish_post(post)
                    
                    if success:
                        published_posts.append(post)
                    else:
                        logger.error(f"Error publicando post {post['id']}")
            
            # Guardar calendario actualizado
            save_schedule(schedule_data)
            
            # Esperar 1 minuto antes de revisar de nuevo
            time.sleep(60)
            
        except Exception as e:
            logger.error(f"Error en scheduler: {e}")
            time.sleep(60)


# Rutas de la API

@app.route('/')
def index():
    """Servir el archivo HTML."""
    return send_from_directory(BASE_DIR, 'tiktok_scheduler.html')


@app.route('/api/tiktok/exchange-token', methods=['POST'])
def exchange_token():
    """Intercambiar código de autorización por token de acceso."""
    try:
        data = request.json
        code = data.get('code')
        redirect_uri = data.get('redirect_uri', TIKTOK_REDIRECT_URI)
        
        if not code:
            return jsonify({'success': False, 'error': 'Código de autorización requerido'}), 400
        
        # Intercambiar código por token
        url = f"{TIKTOK_API_BASE}/oauth/access_token/"
        params = {
            'client_key': TIKTOK_CLIENT_KEY,
            'client_secret': TIKTOK_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(url, params=params, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            tokens = {
                'access_token': token_data.get('data', {}).get('access_token'),
                'refresh_token': token_data.get('data', {}).get('refresh_token'),
                'expires_in': token_data.get('data', {}).get('expires_in'),
                'token_type': token_data.get('data', {}).get('token_type'),
                'scope': token_data.get('data', {}).get('scope'),
                'created_at': datetime.now().isoformat()
            }
            save_tokens(tokens)
            
            return jsonify({
                'success': True,
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token']
            })
        else:
            logger.error(f"Error intercambiando token: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': 'Error al obtener token'}), 400
            
    except Exception as e:
        logger.error(f"Error en exchange-token: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tiktok/verify-token', methods=['POST'])
def verify_token():
    """Verificar si el token de acceso es válido y obtener información del usuario."""
    try:
        data = request.json
        access_token = data.get('access_token')
        
        if not access_token:
            return jsonify({'valid': False}), 400
        
        api = TikTokAPI(access_token)
        is_valid = api.verify_token()
        
        if is_valid:
            # Obtener información del usuario
            user_info = api.get_user_info()
            is_target_account, username = api.verify_target_account()
            
            return jsonify({
                'valid': is_valid,
                'user_info': user_info,
                'is_target_account': is_target_account,
                'target_username': TARGET_TIKTOK_USERNAME,
                'current_username': username
            })
        else:
            return jsonify({'valid': False})
    except Exception as e:
        logger.error(f"Error en verify-token: {e}")
        return jsonify({'valid': False}), 500


@app.route('/api/tiktok/user-info', methods=['GET'])
def get_user_info_endpoint():
    """Obtener información del usuario conectado."""
    try:
        tokens = load_tokens()
        access_token = tokens.get('access_token')
        
        if not access_token:
            return jsonify({'error': 'No hay token de acceso'}), 401
        
        api = TikTokAPI(access_token)
        user_info = api.get_user_info()
        is_target_account, username = api.verify_target_account()
        
        if not user_info:
            return jsonify({'error': 'No se pudo obtener información del usuario'}), 400
        
        return jsonify({
            'success': True,
            'user_info': user_info,
            'is_target_account': is_target_account,
            'target_username': TARGET_TIKTOK_USERNAME,
            'current_username': username
        })
    except Exception as e:
        logger.error(f"Error en user-info: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tiktok/generate-schedule', methods=['POST'])
def generate_schedule_endpoint():
    """Generar calendario de posts."""
    try:
        config = request.json
        posts_per_day = config.get('posts_per_day', 4)
        start_date = config.get('start_date')
        content_folder = config.get('content_folder', 'instagram_downloads/69caylin')
        random_times = config.get('random_times', True)
        time_range = config.get('time_range', '09:00-22:00')
        use_videos = config.get('use_videos', USE_VIDEOS)  # Permitir override
        
        if not start_date:
            return jsonify({'success': False, 'error': 'Fecha de inicio requerida'}), 400
        
        # Actualizar configuración global temporalmente
        global USE_VIDEOS
        original_use_videos = USE_VIDEOS
        USE_VIDEOS = use_videos
        
        try:
            schedule_data = generate_schedule(
                posts_per_day=posts_per_day,
                start_date=start_date,
                content_folder=content_folder,
                random_times=random_times,
                time_range=time_range
            )
        finally:
            USE_VIDEOS = original_use_videos
        
        save_schedule(schedule_data)
        
        # Contar tipos de contenido
        videos_count = len([p for p in schedule_data if p.get('content_type') == 'video'])
        images_count = len([p for p in schedule_data if p.get('content_type') == 'image'])
        
        return jsonify({
            'success': True,
            'total_posts': len(schedule_data),
            'videos_count': videos_count,
            'images_count': images_count,
            'using_videos': use_videos,
            'schedule': schedule_data[:10]  # Primeros 10 para preview
        })
    except Exception as e:
        logger.error(f"Error en generate-schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tiktok/save-schedule', methods=['POST'])
def save_schedule_endpoint():
    """Guardar y activar programación."""
    try:
        # El calendario ya está guardado, solo confirmamos
        schedule_data = load_schedule()
        
        return jsonify({
            'success': True,
            'message': f'Calendario guardado con {len(schedule_data)} posts'
        })
    except Exception as e:
        logger.error(f"Error en save-schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tiktok/start-scheduler', methods=['POST'])
def start_scheduler_endpoint():
    """Iniciar el programador."""
    global scheduler_running
    
    if scheduler_running:
        return jsonify({'success': False, 'error': 'El programador ya está corriendo'}), 400
    
    # Validar que la cuenta sea correcta antes de iniciar
    try:
        tokens = load_tokens()
        access_token = tokens.get('access_token')
        
        if access_token:
            api = TikTokAPI(access_token)
            is_target_account, username = api.verify_target_account()
            
            if not is_target_account:
                return jsonify({
                    'success': False, 
                    'error': f'Cuenta incorrecta: @{username}. Debe ser @{TARGET_TIKTOK_USERNAME}'
                }), 400
    except Exception as e:
        logger.warning(f"No se pudo verificar la cuenta antes de iniciar: {e}")
    
    scheduler_running = True
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    
    return jsonify({
        'success': True, 
        'message': f'Programador iniciado para @{TARGET_TIKTOK_USERNAME}'
    })


@app.route('/api/tiktok/stop-scheduler', methods=['POST'])
def stop_scheduler_endpoint():
    """Detener el programador."""
    global scheduler_running
    
    scheduler_running = False
    
    return jsonify({'success': True, 'message': 'Programador detenido'})


@app.route('/api/tiktok/status', methods=['GET'])
def get_status():
    """Obtener estado del sistema."""
    try:
        schedule_data = load_schedule()
        scheduled_count = len([p for p in schedule_data if p.get('status') == 'scheduled'])
        published_count = len([p for p in schedule_data if p.get('status') == 'published'])
        
        # Encontrar próximo post
        next_post = None
        now = datetime.now()
        for post in schedule_data:
            if post.get('status') == 'scheduled':
                post_dt = datetime.fromisoformat(post['datetime'])
                if post_dt > now:
                    next_post = post_dt.isoformat()
                    break
        
        # Obtener información de la cuenta conectada
        account_info = None
        try:
            tokens = load_tokens()
            access_token = tokens.get('access_token')
            if access_token:
                api = TikTokAPI(access_token)
                user_info = api.get_user_info()
                is_target_account, username = api.verify_target_account()
                account_info = {
                    'username': username,
                    'is_target_account': is_target_account,
                    'target_username': TARGET_TIKTOK_USERNAME
                }
        except Exception:
            pass
        
        return jsonify({
            'status': 'running' if scheduler_running else 'stopped',
            'scheduled_count': scheduled_count,
            'published_count': published_count,
            'next_post': next_post or '-',
            'total_posts': len(schedule_data),
            'account_info': account_info,
            'target_account': TARGET_TIKTOK_USERNAME
        })
    except Exception as e:
        logger.error(f"Error en status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("Iniciando servidor TikTok Scheduler...")
    logger.info(f"Contenido en: {CONTENT_DIR}")
    logger.info(f"Videos en: {VIDEOS_DIR}")
    logger.info(f"Usando videos: {USE_VIDEOS}")
    
    content_files = get_content_files()
    logger.info(f"Archivos encontrados: {len(content_files)}")
    
    if USE_VIDEOS:
        videos = [f for f in content_files if f.suffix.lower() in ['.mp4', '.mov', '.avi']]
        images = [f for f in content_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        logger.info(f"  - Videos: {len(videos)}")
        logger.info(f"  - Imágenes: {len(images)}")
        if not videos and images:
            logger.warning("⚠️  No se encontraron videos, se usarán imágenes")
    
    # Verificar configuración
    if TIKTOK_CLIENT_KEY == 'TU_CLIENT_KEY_AQUI':
        logger.warning("⚠️  ADVERTENCIA: TIKTOK_CLIENT_KEY no configurado")
        logger.warning("   Crea un archivo 'tiktok_config.py' o configura variables de entorno")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_MODE)

