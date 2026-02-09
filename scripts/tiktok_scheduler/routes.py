"""
Flask Routes
============
Rutas de la API Flask refactorizadas.
"""

import logging
import threading
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

from .config import Config
from .tiktok_api import TikTokAPI
from .token_manager import TokenManager
from .schedule_manager import ScheduleManager
from .content_manager import ContentManager
from .schedule_generator import ScheduleGenerator
from .scheduler import Scheduler
from .post_publisher import PostPublisher

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """
    Crear aplicación Flask con rutas.
    
    Returns:
        Instancia de Flask configurada
    """
    app = Flask(__name__)
    CORS(app)
    
    # Inicializar componentes
    token_manager = TokenManager()
    schedule_manager = ScheduleManager()
    content_manager = ContentManager()
    schedule_generator = ScheduleGenerator(content_manager)
    post_publisher = PostPublisher(token_manager)
    scheduler = Scheduler(schedule_manager, post_publisher)
    
    # Variable global para el scheduler
    app.scheduler = scheduler
    
    @app.route('/')
    def index():
        """Servir el archivo HTML."""
        return send_from_directory(Config.BASE_DIR, 'tiktok_scheduler.html')
    
    @app.route('/api/tiktok/exchange-token', methods=['POST'])
    def exchange_token():
        """Intercambiar código de autorización por token de acceso."""
        try:
            data = request.json
            code = data.get('code')
            redirect_uri = data.get('redirect_uri', Config.REDIRECT_URI)
            
            if not code:
                return jsonify({'success': False, 'error': 'Código de autorización requerido'}), 400
            
            # Intercambiar código por token
            url = f"{Config.API_BASE}/oauth/access_token/"
            params = {
                'client_key': Config.CLIENT_KEY,
                'client_secret': Config.CLIENT_SECRET,
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
                token_manager.save(tokens)
                
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
                user_info = api.get_user_info()
                is_target_account, username = api.verify_target_account()
                
                return jsonify({
                    'valid': is_valid,
                    'user_info': user_info,
                    'is_target_account': is_target_account,
                    'target_username': Config.TARGET_USERNAME,
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
            access_token = token_manager.get_access_token()
            
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
                'target_username': Config.TARGET_USERNAME,
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
            use_videos = config.get('use_videos', Config.USE_VIDEOS)
            
            if not start_date:
                return jsonify({'success': False, 'error': 'Fecha de inicio requerida'}), 400
            
            # Crear content manager con configuración
            cm = ContentManager(use_videos=use_videos)
            sg = ScheduleGenerator(cm)
            
            schedule_data = sg.generate_schedule(
                posts_per_day=posts_per_day,
                start_date=start_date,
                random_times=random_times,
                time_range=time_range
            )
            
            schedule_manager.save(schedule_data)
            
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
            schedule_data = schedule_manager.load()
            
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
        if scheduler.is_running():
            return jsonify({'success': False, 'error': 'El programador ya está corriendo'}), 400
        
        # Validar que la cuenta sea correcta antes de iniciar
        try:
            access_token = token_manager.get_access_token()
            
            if access_token:
                api = TikTokAPI(access_token)
                is_target_account, username = api.verify_target_account()
                
                if not is_target_account:
                    return jsonify({
                        'success': False,
                        'error': f'Cuenta incorrecta: @{username}. Debe ser @{Config.TARGET_USERNAME}'
                    }), 400
        except Exception as e:
            logger.warning(f"No se pudo verificar la cuenta antes de iniciar: {e}")
        
        scheduler.start()
        thread = threading.Thread(target=scheduler.run, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Programador iniciado para @{Config.TARGET_USERNAME}'
        })
    
    @app.route('/api/tiktok/stop-scheduler', methods=['POST'])
    def stop_scheduler_endpoint():
        """Detener el programador."""
        scheduler.stop()
        return jsonify({'success': True, 'message': 'Programador detenido'})
    
    @app.route('/api/tiktok/status', methods=['GET'])
    def get_status():
        """Obtener estado del sistema."""
        try:
            stats = schedule_manager.get_statistics()
            next_post = stats.get('next_post')
            
            # Obtener información de la cuenta conectada
            account_info = None
            try:
                access_token = token_manager.get_access_token()
                if access_token:
                    api = TikTokAPI(access_token)
                    user_info = api.get_user_info()
                    is_target_account, username = api.verify_target_account()
                    account_info = {
                        'username': username,
                        'is_target_account': is_target_account,
                        'target_username': Config.TARGET_USERNAME
                    }
            except Exception:
                pass
            
            return jsonify({
                'status': 'running' if scheduler.is_running() else 'stopped',
                'scheduled_count': stats['scheduled'],
                'published_count': stats['published'],
                'next_post': next_post['datetime'] if next_post else '-',
                'total_posts': stats['total'],
                'account_info': account_info,
                'target_account': Config.TARGET_USERNAME
            })
        except Exception as e:
            logger.error(f"Error en status: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    return app







