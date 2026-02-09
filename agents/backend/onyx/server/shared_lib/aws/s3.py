"""
AWS S3 Manager
==============

Gestor para AWS S3 con:
- Upload/Download
- Presigned URLs
- Multipart uploads
- Lifecycle policies
- Versioning
"""

import logging
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None


class S3Manager:
    """Gestor para AWS S3"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.client = None
        self._setup()
    
    def _setup(self):
        """Configura cliente de S3"""
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 no disponible. Instala con: pip install boto3")
            return
        
        try:
            self.client = boto3.client('s3', region_name=self.region)
            logger.info(f"S3 configurado para región: {self.region}")
        except Exception as e:
            logger.error(f"Error configurando S3: {e}")
    
    def upload_file(
        self,
        bucket: str,
        key: str,
        file_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Sube un archivo a S3
        
        Args:
            bucket: Nombre del bucket
            key: Clave (path) del archivo
            file_path: Ruta local del archivo
            content_type: Tipo de contenido
            metadata: Metadatos adicionales
            
        Returns:
            True si éxito, False si falla
        """
        if not self.client:
            return False
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.client.upload_file(
                file_path,
                bucket,
                key,
                ExtraArgs=extra_args if extra_args else None
            )
            
            logger.info(f"Archivo subido: s3://{bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Error subiendo archivo: {e}")
            return False
    
    def upload_fileobj(
        self,
        bucket: str,
        key: str,
        file_obj: BinaryIO,
        content_type: Optional[str] = None
    ) -> bool:
        """
        Sube un file object a S3
        
        Args:
            bucket: Nombre del bucket
            key: Clave del archivo
            file_obj: File object (BytesIO, etc.)
            content_type: Tipo de contenido
            
        Returns:
            True si éxito, False si falla
        """
        if not self.client:
            return False
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_fileobj(
                file_obj,
                bucket,
                key,
                ExtraArgs=extra_args if extra_args else None
            )
            
            logger.info(f"File object subido: s3://{bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Error subiendo file object: {e}")
            return False
    
    def download_file(
        self,
        bucket: str,
        key: str,
        file_path: str
    ) -> bool:
        """
        Descarga un archivo de S3
        
        Args:
            bucket: Nombre del bucket
            key: Clave del archivo
            file_path: Ruta local donde guardar
            
        Returns:
            True si éxito, False si falla
        """
        if not self.client:
            return False
        
        try:
            self.client.download_file(bucket, key, file_path)
            logger.info(f"Archivo descargado: {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Error descargando archivo: {e}")
            return False
    
    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600,
        http_method: str = "GET"
    ) -> Optional[str]:
        """
        Genera una URL presignada
        
        Args:
            bucket: Nombre del bucket
            key: Clave del archivo
            expiration: Tiempo de expiración en segundos
            http_method: Método HTTP (GET, PUT, etc.)
            
        Returns:
            URL presignada o None si falla
        """
        if not self.client:
            return None
        
        try:
            url = self.client.generate_presigned_url(
                'get_object' if http_method == "GET" else 'put_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            
            logger.info(f"URL presignada generada para: s3://{bucket}/{key}")
            return url
        except ClientError as e:
            logger.error(f"Error generando URL presignada: {e}")
            return None
    
    def delete_object(
        self,
        bucket: str,
        key: str
    ) -> bool:
        """
        Elimina un objeto de S3
        
        Args:
            bucket: Nombre del bucket
            key: Clave del objeto
            
        Returns:
            True si éxito, False si falla
        """
        if not self.client:
            return False
        
        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"Objeto eliminado: s3://{bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Error eliminando objeto: {e}")
            return False
    
    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Lista objetos en S3
        
        Args:
            bucket: Nombre del bucket
            prefix: Prefijo para filtrar
            max_keys: Máximo de objetos a retornar
            
        Returns:
            Lista de objetos
        """
        if not self.client:
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"Error listando objetos: {e}")
            return []


# Instancia global
s3_manager = S3Manager()




