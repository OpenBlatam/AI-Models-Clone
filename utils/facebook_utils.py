"""
🎯 Facebook Utils
================

Utilidades para procesamiento y optimización de Facebook posts.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib


logger = logging.getLogger(__name__)


class FacebookUtils:
    """Utilidades para Facebook posts."""
    
    @staticmethod
    def extract_hashtags(content: str) -> List[str]:
        """Extraer hashtags del contenido."""
        try:
            # Pattern para hashtags válidos de Facebook
            hashtag_pattern = r'#[a-zA-Z0-9_áéíóúñÁÉÍÓÚÑ]+(?=[^a-zA-Z0-9_áéíóúñÁÉÍÓÚÑ]|$)'
            hashtags = re.findall(hashtag_pattern, content)
            
            # Limpiar y validar hashtags
            cleaned_hashtags = []
            for hashtag in hashtags:
                # Remover el # inicial para almacenamiento
                clean_tag = hashtag[1:]
                if len(clean_tag) >= 2 and len(clean_tag) <= 30:  # Facebook limits
                    cleaned_hashtags.append(clean_tag)
            
            return cleaned_hashtags
            
        except Exception as e:
            logger.error(f"Error extracting hashtags: {e}")
            return []
    
    @staticmethod
    def extract_mentions(content: str) -> List[str]:
        """Extraer menciones (@) del contenido."""
        try:
            # Pattern para menciones válidas de Facebook
            mention_pattern = r'@[a-zA-Z0-9._]+(?=[^a-zA-Z0-9._]|$)'
            mentions = re.findall(mention_pattern, content)
            
            # Limpiar menciones
            cleaned_mentions = []
            for mention in mentions:
                # Remover el @ inicial para almacenamiento
                clean_mention = mention[1:]
                if len(clean_mention) >= 1 and len(clean_mention) <= 50:
                    cleaned_mentions.append(clean_mention)
            
            return cleaned_mentions
            
        except Exception as e:
            logger.error(f"Error extracting mentions: {e}")
            return []
    
    @staticmethod
    def clean_content_for_display(content: str, separate_hashtags: bool = True) -> str:
        """Limpiar contenido para display."""
        try:
            cleaned_content = content.strip()
            
            if separate_hashtags:
                # Remover hashtags del contenido principal si se mostrarán por separado
                hashtag_pattern = r'#[a-zA-Z0-9_áéíóúñÁÉÍÓÚÑ]+(?=\s|$)'
                cleaned_content = re.sub(hashtag_pattern, '', cleaned_content)
                
                # Limpiar espacios múltiples
                cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                cleaned_content = cleaned_content.strip()
            
            return cleaned_content
            
        except Exception as e:
            logger.error(f"Error cleaning content: {e}")
            return content
    
    @staticmethod
    def validate_post_length(content: str, max_length: int = 2000) -> Tuple[bool, int]:
        """Validar longitud del post."""
        try:
            char_count = len(content)
            is_valid = char_count <= max_length
            return is_valid, char_count
            
        except Exception as e:
            logger.error(f"Error validating post length: {e}")
            return False, 0
    
    @staticmethod
    def analyze_post_structure(content: str) -> Dict[str, Any]:
        """Analizar estructura del post."""
        try:
            analysis = {
                'character_count': len(content),
                'word_count': len(content.split()),
                'sentence_count': len(re.findall(r'[.!?]+', content)),
                'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
                'line_count': len([line for line in content.split('\n') if line.strip()]),
                'hashtag_count': len(FacebookUtils.extract_hashtags(content)),
                'mention_count': len(FacebookUtils.extract_mentions(content)),
                'emoji_count': FacebookUtils.count_emojis(content),
                'url_count': len(FacebookUtils.extract_urls(content)),
                'has_question': '?' in content,
                'has_exclamation': '!' in content,
                'has_call_to_action': FacebookUtils.detect_call_to_action(content)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing post structure: {e}")
            return {}
    
    @staticmethod
    def count_emojis(content: str) -> int:
        """Contar emojis en el contenido."""
        try:
            # Pattern básico para emojis (caracteres Unicode fuera del rango ASCII)
            emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F]|'  # emoticons
                                        r'[\U0001F300-\U0001F5FF]|'  # symbols & pictographs
                                        r'[\U0001F680-\U0001F6FF]|'  # transport & map
                                        r'[\U0001F1E0-\U0001F1FF]',  # flags
                                        content))
            return emoji_count
            
        except Exception as e:
            logger.error(f"Error counting emojis: {e}")
            return 0
    
    @staticmethod
    def extract_urls(content: str) -> List[str]:
        """Extraer URLs del contenido."""
        try:
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, content)
            return urls
            
        except Exception as e:
            logger.error(f"Error extracting URLs: {e}")
            return []
    
    @staticmethod
    def detect_call_to_action(content: str) -> bool:
        """Detectar call-to-action en el contenido."""
        try:
            cta_patterns = [
                r'\b(click|tap|swipe|visit|go to|check out|learn more|read more)\b',
                r'\b(buy now|shop now|order now|get yours|purchase)\b',
                r'\b(sign up|register|subscribe|follow|join)\b',
                r'\b(download|install|try|start)\b',
                r'\b(comment|share|like|tag|mention)\b',
                r'\b(call|contact|email|message)\b'
            ]
            
            for pattern in cta_patterns:
                if re.search(pattern, content.lower()):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting call to action: {e}")
            return False
    
    @staticmethod
    def optimize_hashtags(hashtags: List[str], max_hashtags: int = 5) -> List[str]:
        """Optimizar lista de hashtags."""
        try:
            # Filtrar hashtags duplicados y muy cortos
            unique_hashtags = []
            seen = set()
            
            for hashtag in hashtags:
                clean_hashtag = hashtag.lower().strip()
                if (len(clean_hashtag) >= 2 and 
                    clean_hashtag not in seen and 
                    len(unique_hashtags) < max_hashtags):
                    unique_hashtags.append(hashtag)
                    seen.add(clean_hashtag)
            
            return unique_hashtags
            
        except Exception as e:
            logger.error(f"Error optimizing hashtags: {e}")
            return hashtags[:max_hashtags]
    
    @staticmethod
    def calculate_readability_score(content: str) -> float:
        """Calcular score de legibilidad (0.0 - 1.0)."""
        try:
            # Métricas básicas de legibilidad
            words = content.split()
            sentences = re.split(r'[.!?]+', content)
            
            if not words or not sentences:
                return 0.0
            
            # Calcular métricas
            avg_words_per_sentence = len(words) / len([s for s in sentences if s.strip()])
            avg_chars_per_word = sum(len(word) for word in words) / len(words)
            
            # Score basado en heurísticas
            score = 1.0
            
            # Penalizar oraciones muy largas
            if avg_words_per_sentence > 20:
                score -= 0.3
            elif avg_words_per_sentence > 15:
                score -= 0.1
            
            # Penalizar palabras muy largas
            if avg_chars_per_word > 8:
                score -= 0.2
            elif avg_chars_per_word > 6:
                score -= 0.1
            
            # Bonificar uso de emojis (mejora legibilidad visual)
            emoji_count = FacebookUtils.count_emojis(content)
            if emoji_count > 0 and emoji_count <= 5:
                score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating readability score: {e}")
            return 0.5
    
    @staticmethod
    def predict_optimal_times() -> List[datetime]:
        """Predecir horas óptimas de publicación."""
        try:
            now = datetime.now()
            optimal_times = []
            
            # Horas típicamente óptimas para Facebook
            optimal_hours = [9, 14, 15, 19, 20]  # 9am, 2pm, 3pm, 7pm, 8pm
            
            for hour in optimal_hours:
                # Próxima ocurrencia de cada hora
                optimal_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
                if optimal_time <= now:
                    optimal_time += timedelta(days=1)
                
                optimal_times.append(optimal_time)
            
            return sorted(optimal_times)
            
        except Exception as e:
            logger.error(f"Error predicting optimal times: {e}")
            return []
    
    @staticmethod
    def generate_content_hash(content: str, post_type: str = "text") -> str:
        """Generar hash único para el contenido."""
        try:
            # Crear string único combinando contenido y tipo
            unique_string = f"{content}_{post_type}_{datetime.now().isoformat()}"
            
            # Generar hash MD5
            content_hash = hashlib.md5(unique_string.encode()).hexdigest()
            
            return content_hash
            
        except Exception as e:
            logger.error(f"Error generating content hash: {e}")
            return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def format_engagement_metrics(likes: int, shares: int, comments: int) -> Dict[str, str]:
        """Formatear métricas de engagement para display."""
        try:
            def format_number(num):
                if num >= 1000000:
                    return f"{num/1000000:.1f}M"
                elif num >= 1000:
                    return f"{num/1000:.1f}K"
                else:
                    return str(num)
            
            return {
                'likes_formatted': format_number(likes),
                'shares_formatted': format_number(shares),
                'comments_formatted': format_number(comments),
                'total_engagement': format_number(likes + shares + comments)
            }
            
        except Exception as e:
            logger.error(f"Error formatting engagement metrics: {e}")
            return {
                'likes_formatted': str(likes),
                'shares_formatted': str(shares),
                'comments_formatted': str(comments),
                'total_engagement': str(likes + shares + comments)
            }
    
    @staticmethod
    def validate_facebook_compliance(content: str) -> Dict[str, Any]:
        """Validar cumplimiento con políticas de Facebook."""
        try:
            issues = []
            warnings = []
            
            # Verificar longitud
            if len(content) > 2000:
                issues.append("Content exceeds Facebook's 2000 character limit")
            
            # Verificar spam indicators
            if content.count('!') > 5:
                warnings.append("Excessive use of exclamation marks may be flagged as spam")
            
            if len(re.findall(r'[A-Z]{3,}', content)) > 3:
                warnings.append("Excessive use of capital letters may be flagged as spam")
            
            # Verificar hashtags excesivos
            hashtag_count = len(FacebookUtils.extract_hashtags(content))
            if hashtag_count > 10:
                warnings.append("Too many hashtags may reduce organic reach")
            
            # Verificar palabras prohibidas comunes
            prohibited_patterns = [
                r'\b(click here|free money|guaranteed|limited time)\b',
                r'\b(lose weight fast|miracle cure|get rich quick)\b'
            ]
            
            for pattern in prohibited_patterns:
                if re.search(pattern, content.lower()):
                    warnings.append("Content may contain spam-like language")
                    break
            
            compliance_score = 1.0 - (len(issues) * 0.3) - (len(warnings) * 0.1)
            compliance_score = max(0.0, compliance_score)
            
            return {
                'is_compliant': len(issues) == 0,
                'compliance_score': compliance_score,
                'issues': issues,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.error(f"Error validating Facebook compliance: {e}")
            return {
                'is_compliant': True,
                'compliance_score': 1.0,
                'issues': [],
                'warnings': ['Could not validate compliance']
            } 