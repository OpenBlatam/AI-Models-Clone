"""
AWS DynamoDB Manager
====================

Gestor optimizado para DynamoDB con:
- Operaciones CRUD
- Queries y scans optimizados
- Batch operations
- Connection pooling
- Retry logic
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    Key = None
    Attr = None


class DynamoDBManager:
    """Gestor para AWS DynamoDB"""
    
    def __init__(
        self,
        region: str = "us-east-1",
        table_prefix: str = "",
        max_retries: int = 3
    ):
        self.region = region
        self.table_prefix = table_prefix
        self.max_retries = max_retries
        self.client = None
        self.resource = None
        self._setup()
    
    def _setup(self):
        """Configura cliente y resource de DynamoDB"""
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 no disponible. Instala con: pip install boto3")
            return
        
        try:
            # Cliente para operaciones de bajo nivel
            self.client = boto3.client(
                'dynamodb',
                region_name=self.region,
                max_attempts=self.max_retries
            )
            
            # Resource para operaciones de alto nivel
            self.resource = boto3.resource(
                'dynamodb',
                region_name=self.region
            )
            
            logger.info(f"DynamoDB configurado para región: {self.region}")
        except Exception as e:
            logger.error(f"Error configurando DynamoDB: {e}")
    
    def get_table(self, table_name: str):
        """Obtiene referencia a una tabla"""
        if not self.resource:
            return None
        
        full_name = f"{self.table_prefix}{table_name}" if self.table_prefix else table_name
        return self.resource.Table(full_name)
    
    async def get_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        consistent_read: bool = False
    ) -> Optional[Dict]:
        """
        Obtiene un item de DynamoDB
        
        Args:
            table_name: Nombre de la tabla
            key: Clave del item (dict con partition key y sort key si aplica)
            consistent_read: Si usar consistent read
            
        Returns:
            Item como dict o None si no existe
        """
        if not self.resource:
            return None
        
        try:
            table = self.get_table(table_name)
            response = table.get_item(
                Key=key,
                ConsistentRead=consistent_read
            )
            
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Error obteniendo item: {e}")
            return None
    
    async def put_item(
        self,
        table_name: str,
        item: Dict[str, Any],
        condition_expression: Optional[str] = None
    ) -> bool:
        """
        Guarda un item en DynamoDB
        
        Args:
            table_name: Nombre de la tabla
            item: Item a guardar
            condition_expression: Expresión de condición opcional
            
        Returns:
            True si éxito, False si falla
        """
        if not self.resource:
            return False
        
        try:
            table = self.get_table(table_name)
            
            # Agregar timestamps
            item['updated_at'] = datetime.utcnow().isoformat()
            if 'created_at' not in item:
                item['created_at'] = item['updated_at']
            
            kwargs = {'Item': item}
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            
            table.put_item(**kwargs)
            return True
        except ClientError as e:
            logger.error(f"Error guardando item: {e}")
            return False
    
    async def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_attribute_values: Dict[str, Any],
        expression_attribute_names: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Actualiza un item en DynamoDB
        
        Args:
            table_name: Nombre de la tabla
            key: Clave del item
            update_expression: Expresión de actualización
            expression_attribute_values: Valores para la expresión
            expression_attribute_names: Nombres de atributos (para palabras reservadas)
            
        Returns:
            True si éxito, False si falla
        """
        if not self.resource:
            return False
        
        try:
            table = self.get_table(table_name)
            
            # Agregar updated_at
            if 'updated_at' not in expression_attribute_values:
                expression_attribute_values[':updated_at'] = datetime.utcnow().isoformat()
                update_expression += ", updated_at = :updated_at"
            
            kwargs = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_attribute_values
            }
            
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
            table.update_item(**kwargs)
            return True
        except ClientError as e:
            logger.error(f"Error actualizando item: {e}")
            return False
    
    async def delete_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        condition_expression: Optional[str] = None
    ) -> bool:
        """
        Elimina un item de DynamoDB
        
        Args:
            table_name: Nombre de la tabla
            key: Clave del item
            condition_expression: Expresión de condición opcional
            
        Returns:
            True si éxito, False si falla
        """
        if not self.resource:
            return False
        
        try:
            table = self.get_table(table_name)
            
            kwargs = {'Key': key}
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            
            table.delete_item(**kwargs)
            return True
        except ClientError as e:
            logger.error(f"Error eliminando item: {e}")
            return False
    
    async def query(
        self,
        table_name: str,
        key_condition_expression: Any,
        filter_expression: Optional[Any] = None,
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        exclusive_start_key: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query a DynamoDB
        
        Args:
            table_name: Nombre de la tabla
            key_condition_expression: Condición de clave (usar Key())
            filter_expression: Filtro adicional (usar Attr())
            index_name: Nombre del índice GSI/LSI
            limit: Límite de resultados
            exclusive_start_key: Key para paginación
            
        Returns:
            Lista de items
        """
        if not self.resource or not Key:
            return []
        
        try:
            table = self.get_table(table_name)
            
            kwargs = {
                'KeyConditionExpression': key_condition_expression
            }
            
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            
            if index_name:
                kwargs['IndexName'] = index_name
            
            if limit:
                kwargs['Limit'] = limit
            
            if exclusive_start_key:
                kwargs['ExclusiveStartKey'] = exclusive_start_key
            
            response = table.query(**kwargs)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"Error en query: {e}")
            return []
    
    async def scan(
        self,
        table_name: str,
        filter_expression: Optional[Any] = None,
        limit: Optional[int] = None,
        exclusive_start_key: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Scan a DynamoDB (menos eficiente que query)
        
        Args:
            table_name: Nombre de la tabla
            filter_expression: Filtro (usar Attr())
            limit: Límite de resultados
            exclusive_start_key: Key para paginación
            
        Returns:
            Lista de items
        """
        if not self.resource:
            return []
        
        try:
            table = self.get_table(table_name)
            
            kwargs = {}
            
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            
            if limit:
                kwargs['Limit'] = limit
            
            if exclusive_start_key:
                kwargs['ExclusiveStartKey'] = exclusive_start_key
            
            response = table.scan(**kwargs)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"Error en scan: {e}")
            return []
    
    async def batch_get_items(
        self,
        table_name: str,
        keys: List[Dict[str, Any]]
    ) -> List[Dict]:
        """
        Obtiene múltiples items en batch
        
        Args:
            table_name: Nombre de la tabla
            keys: Lista de claves
            
        Returns:
            Lista de items
        """
        if not self.resource:
            return []
        
        try:
            table = self.get_table(table_name)
            
            # DynamoDB permite máximo 100 items por batch
            batch_size = 100
            all_items = []
            
            for i in range(0, len(keys), batch_size):
                batch_keys = keys[i:i + batch_size]
                
                response = self.client.batch_get_item(
                    RequestItems={
                        table.name: {
                            'Keys': batch_keys
                        }
                    }
                )
                
                items = response.get('Responses', {}).get(table.name, [])
                all_items.extend(items)
            
            return all_items
        except ClientError as e:
            logger.error(f"Error en batch get: {e}")
            return []
    
    async def batch_write_items(
        self,
        table_name: str,
        items: List[Dict[str, Any]]
    ) -> bool:
        """
        Escribe múltiples items en batch
        
        Args:
            table_name: Nombre de la tabla
            items: Lista de items a escribir
            
        Returns:
            True si éxito, False si falla
        """
        if not self.resource:
            return False
        
        try:
            table = self.get_table(table_name)
            
            # DynamoDB permite máximo 25 items por batch
            batch_size = 25
            
            for i in range(0, len(items), batch_size):
                batch_items = items[i:i + batch_size]
                
                with table.batch_writer() as batch:
                    for item in batch_items:
                        # Agregar timestamps
                        item['updated_at'] = datetime.utcnow().isoformat()
                        if 'created_at' not in item:
                            item['created_at'] = item['updated_at']
                        
                        batch.put_item(Item=item)
            
            return True
        except ClientError as e:
            logger.error(f"Error en batch write: {e}")
            return False


# Instancia global
dynamodb_manager = DynamoDBManager()




