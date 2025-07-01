"""
🔌 CONFIG INTERFACES - Contratos para Configuración
==================================================

Interfaces para servicios de configuración y gestión de parámetros.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from ..core.enums import ProcessingTier, CacheStrategy, Environment, LogLevel


class IConfigurationService(ABC):
    """Interface para servicio de configuración."""
    
    @abstractmethod
    def get_processing_tier(self) -> ProcessingTier:
        """
        Obtener tier de procesamiento por defecto.
        
        Returns:
            ProcessingTier configurado
        """
        pass
    
    @abstractmethod
    def get_cache_strategy(self) -> CacheStrategy:
        """
        Obtener estrategia de cache configurada.
        
        Returns:
            CacheStrategy activa
        """
        pass
    
    @abstractmethod
    def is_optimization_enabled(self, optimization: str) -> bool:
        """
        Verificar si una optimización está habilitada.
        
        Args:
            optimization: Nombre de la optimización
            
        Returns:
            True si está habilitada
        """
        pass
    
    @abstractmethod
    def get_environment(self) -> Environment:
        """
        Obtener entorno actual.
        
        Returns:
            Environment configurado
        """
        pass
    
    @abstractmethod
    def get_log_level(self) -> LogLevel:
        """
        Obtener nivel de logging.
        
        Returns:
            LogLevel configurado
        """
        pass
    
    @abstractmethod
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Obtener valor de configuración por clave.
        
        Args:
            key: Clave de configuración
            default: Valor por defecto
            
        Returns:
            Valor configurado o default
        """
        pass
    
    @abstractmethod
    def set_config_value(self, key: str, value: Any) -> None:
        """
        Establecer valor de configuración.
        
        Args:
            key: Clave de configuración
            value: Nuevo valor
        """
        pass
    
    @abstractmethod
    def get_all_config(self) -> Dict[str, Any]:
        """
        Obtener toda la configuración.
        
        Returns:
            Diccionario con toda la configuración
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> List[str]:
        """
        Validar configuración actual.
        
        Returns:
            Lista de errores de validación (vacía si es válida)
        """
        pass
    
    @abstractmethod
    def reload_config(self) -> bool:
        """
        Recargar configuración desde fuente.
        
        Returns:
            True si se recargó correctamente
        """
        pass


class IEnvironmentConfigLoader(ABC):
    """Interface para cargar configuración desde entorno."""
    
    @abstractmethod
    def load_from_environment(self) -> Dict[str, Any]:
        """
        Cargar configuración desde variables de entorno.
        
        Returns:
            Diccionario con configuración cargada
        """
        pass
    
    @abstractmethod
    def get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtener variable de entorno.
        
        Args:
            key: Nombre de la variable
            default: Valor por defecto
            
        Returns:
            Valor de la variable o default
        """
        pass
    
    @abstractmethod
    def get_required_env_vars(self) -> List[str]:
        """
        Obtener lista de variables de entorno requeridas.
        
        Returns:
            Lista de variables requeridas
        """
        pass
    
    @abstractmethod
    def validate_env_vars(self) -> Dict[str, str]:
        """
        Validar variables de entorno.
        
        Returns:
            Diccionario de variable -> error (vacío si todas son válidas)
        """
        pass


class IFileConfigLoader(ABC):
    """Interface para cargar configuración desde archivos."""
    
    @abstractmethod
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Cargar configuración desde archivo.
        
        Args:
            file_path: Ruta del archivo de configuración
            
        Returns:
            Diccionario con configuración cargada
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Obtener formatos de archivo soportados.
        
        Returns:
            Lista de extensiones soportadas
        """
        pass
    
    @abstractmethod
    def validate_config_file(self, file_path: str) -> bool:
        """
        Validar archivo de configuración.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            True si el archivo es válido
        """
        pass
    
    @abstractmethod
    def watch_config_file(self, file_path: str, callback: callable) -> None:
        """
        Observar cambios en archivo de configuración.
        
        Args:
            file_path: Ruta del archivo a observar
            callback: Función a llamar cuando cambie
        """
        pass


class ISecretManager(ABC):
    """Interface para gestión de secretos."""
    
    @abstractmethod
    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Obtener secreto por nombre.
        
        Args:
            secret_name: Nombre del secreto
            
        Returns:
            Valor del secreto o None si no existe
        """
        pass
    
    @abstractmethod
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Establecer secreto.
        
        Args:
            secret_name: Nombre del secreto
            secret_value: Valor del secreto
            
        Returns:
            True si se estableció correctamente
        """
        pass
    
    @abstractmethod
    def delete_secret(self, secret_name: str) -> bool:
        """
        Eliminar secreto.
        
        Args:
            secret_name: Nombre del secreto
            
        Returns:
            True si se eliminó correctamente
        """
        pass
    
    @abstractmethod
    def list_secrets(self) -> List[str]:
        """
        Listar nombres de secretos disponibles.
        
        Returns:
            Lista de nombres de secretos
        """
        pass
    
    @abstractmethod
    def rotate_secret(self, secret_name: str) -> str:
        """
        Rotar secreto (generar nuevo valor).
        
        Args:
            secret_name: Nombre del secreto
            
        Returns:
            Nuevo valor del secreto
        """
        pass


class IConfigValidator(ABC):
    """Interface para validación de configuración."""
    
    @abstractmethod
    def validate_section(self, section_name: str, config: Dict[str, Any]) -> List[str]:
        """
        Validar sección específica de configuración.
        
        Args:
            section_name: Nombre de la sección
            config: Configuración a validar
            
        Returns:
            Lista de errores de validación
        """
        pass
    
    @abstractmethod
    def validate_data_types(self, config: Dict[str, Any]) -> List[str]:
        """
        Validar tipos de datos en configuración.
        
        Args:
            config: Configuración a validar
            
        Returns:
            Lista de errores de tipos
        """
        pass
    
    @abstractmethod
    def validate_ranges(self, config: Dict[str, Any]) -> List[str]:
        """
        Validar rangos de valores.
        
        Args:
            config: Configuración a validar
            
        Returns:
            Lista de errores de rangos
        """
        pass
    
    @abstractmethod
    def validate_dependencies(self, config: Dict[str, Any]) -> List[str]:
        """
        Validar dependencias entre configuraciones.
        
        Args:
            config: Configuración a validar
            
        Returns:
            Lista de errores de dependencias
        """
        pass
    
    @abstractmethod
    def get_validation_schema(self) -> Dict[str, Any]:
        """
        Obtener esquema de validación.
        
        Returns:
            Esquema de validación
        """
        pass


class IConfigMerger(ABC):
    """Interface para fusión de configuraciones."""
    
    @abstractmethod
    def merge_configs(
        self, 
        base_config: Dict[str, Any], 
        override_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fusionar configuraciones.
        
        Args:
            base_config: Configuración base
            override_config: Configuración que sobrescribe
            
        Returns:
            Configuración fusionada
        """
        pass
    
    @abstractmethod
    def merge_with_environment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fusionar configuración con variables de entorno.
        
        Args:
            config: Configuración base
            
        Returns:
            Configuración fusionada con entorno
        """
        pass
    
    @abstractmethod
    def set_merge_strategy(self, strategy: str) -> None:
        """
        Establecer estrategia de fusión.
        
        Args:
            strategy: Estrategia (replace, merge, append, etc.)
        """
        pass
    
    @abstractmethod
    def get_merge_conflicts(
        self, 
        config1: Dict[str, Any], 
        config2: Dict[str, Any]
    ) -> List[str]:
        """
        Obtener conflictos en fusión.
        
        Args:
            config1: Primera configuración
            config2: Segunda configuración
            
        Returns:
            Lista de claves en conflicto
        """
        pass


class IConfigTransformer(ABC):
    """Interface para transformación de configuración."""
    
    @abstractmethod
    def transform_for_environment(
        self, 
        config: Dict[str, Any], 
        target_env: Environment
    ) -> Dict[str, Any]:
        """
        Transformar configuración para entorno específico.
        
        Args:
            config: Configuración base
            target_env: Entorno objetivo
            
        Returns:
            Configuración transformada
        """
        pass
    
    @abstractmethod
    def apply_environment_overrides(
        self, 
        config: Dict[str, Any], 
        environment: Environment
    ) -> Dict[str, Any]:
        """
        Aplicar overrides específicos del entorno.
        
        Args:
            config: Configuración base
            environment: Entorno actual
            
        Returns:
            Configuración con overrides aplicados
        """
        pass
    
    @abstractmethod
    def substitute_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sustituir variables en configuración.
        
        Args:
            config: Configuración con variables
            
        Returns:
            Configuración con variables sustituidas
        """
        pass
    
    @abstractmethod
    def normalize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizar configuración (tipos, nombres, etc.).
        
        Args:
            config: Configuración a normalizar
            
        Returns:
            Configuración normalizada
        """
        pass 