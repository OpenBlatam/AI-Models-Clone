"""
Code Explanation Model - Modelo refactorizado para explicar código
==================================================================

Modelo para generar explicaciones de código en lenguaje natural usando
modelos seq2seq de transformers (T5, BART, etc.).

Refactorizado con:
- Sistema de cache unificado
- Validaciones consistentes
- Métodos organizados y sin duplicación
- Type hints completos
- Mejor manejo de errores
"""

import hashlib
import logging
from typing import Dict, Any, Optional, List
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig

from .base import BaseModel

logger = logging.getLogger(__name__)


class CodeExplanationModel(BaseModel):
    """
    Modelo para explicar código usando modelos seq2seq.
    
    Utiliza modelos como T5 para generar explicaciones en lenguaje natural
    a partir de código fuente.
    """
    
    # Templates de prompts por nivel de detalle
    PROMPT_TEMPLATES = {
        "brief": "Briefly explain this {language} code: {code}",
        "medium": "Explain this {language} code: {code}",
        "detailed": "Provide a detailed explanation of this {language} code, "
                   "including what each part does: {code}"
    }
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Inicializar modelo de explicación de código.
        
        Args:
            config: Diccionario de configuración con:
                - model_name: Nombre del modelo (default: "t5-small")
                - max_length: Longitud máxima de entrada (default: 512)
                - max_target_length: Longitud máxima de salida (default: 128)
                - enable_cache: Habilitar caché (default: True)
                - cache_ttl: TTL del caché en segundos (default: 3600)
                - cache_instance: Instancia de caché externa (opcional)
                - prompt_template: Template del prompt (default: "Explain this code: {code}")
        
        Raises:
            ValueError: Si los parámetros de configuración son inválidos
        """
        super().__init__(config)
        
        # Validar y asignar configuración
        self.model_name: str = self._validate_model_name(config.get("model_name", "t5-small"))
        self.max_length: int = self._validate_positive_int(config.get("max_length", 512), "max_length")
        self.max_target_length: int = self._validate_positive_int(
            config.get("max_target_length", 128), "max_target_length"
        )
        self.prompt_template: str = config.get("prompt_template", "Explain this code: {code}")
        
        # Configuración de caché
        self.enable_cache: bool = config.get("enable_cache", True)
        self.cache_ttl: float = max(0.0, float(config.get("cache_ttl", 3600.0)))
        self._cache: Optional[Any] = config.get("cache_instance")
        self._explanation_cache: Dict[str, str] = {}  # Cache interno simple
        
        # Modelo y tokenizer
        self.model: Optional[AutoModelForSeq2SeqLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self._initialized: bool = False
        
        # Estadísticas
        self._stats: Dict[str, int] = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
    
    @staticmethod
    def _validate_model_name(model_name: Any) -> str:
        """Validar nombre del modelo."""
        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("model_name must be a non-empty string")
        return model_name.strip()
    
    @staticmethod
    def _validate_positive_int(value: Any, name: str) -> int:
        """Validar entero positivo."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer, got {value}")
        return value
    
    def _validate_code(self, code: Any) -> str:
        """
        Validar código de entrada.
        
        Args:
            code: Código a validar
            
        Returns:
            Código validado
            
        Raises:
            ValueError: Si el código no es válido
        """
        if not isinstance(code, str):
            raise ValueError(f"code must be a string, got {type(code)}")
        
        code = code.strip()
        if not code:
            raise ValueError("code cannot be empty")
        
        # Validar longitud aproximada (4 caracteres por token)
        max_chars = self.max_length * 4
        if len(code) > max_chars:
            raise ValueError(
                f"code too long: {len(code)} characters. "
                f"Maximum: {max_chars} characters"
            )
        
        return code
    
    def _validate_generation_params(
        self,
        temperature: Any,
        num_beams: Any,
        max_length: Optional[Any] = None
    ) -> None:
        """Validar parámetros de generación."""
        if not isinstance(temperature, (int, float)) or temperature < 0:
            raise ValueError(f"temperature must be non-negative, got {temperature}")
        
        if not isinstance(num_beams, int) or num_beams < 1:
            raise ValueError(f"num_beams must be a positive integer, got {num_beams}")
        
        if max_length is not None:
            self._validate_positive_int(max_length, "max_length")
    
    def _get_cache_key(self, code: str, **kwargs: Any) -> str:
        """
        Generar clave de caché para código y parámetros.
        
        Args:
            code: Código
            **kwargs: Parámetros adicionales
            
        Returns:
            Clave hash para el caché
        """
        # Ordenar kwargs para consistencia
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{code}|{sorted_kwargs}"
        return hashlib.sha256(key_data.encode('utf-8')).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """
        Obtener explicación del caché.
        
        Args:
            cache_key: Clave del caché
            
        Returns:
            Explicación cacheada o None
        """
        if not self.enable_cache:
            return None
        
        # Intentar caché externo primero
        if self._cache is not None:
            try:
                if hasattr(self._cache, "get"):
                    result = self._cache.get(cache_key)
                    if result is not None:
                        self._stats["cache_hits"] += 1
                        return result
            except Exception as e:
                logger.warning(f"External cache error: {e}")
        
        # Intentar caché interno
        if cache_key in self._explanation_cache:
            self._stats["cache_hits"] += 1
            return self._explanation_cache[cache_key]
        
        self._stats["cache_misses"] += 1
        return None
    
    def _save_to_cache(self, cache_key: str, explanation: str) -> None:
        """
        Guardar explicación en caché.
        
        Args:
            cache_key: Clave del caché
            explanation: Explicación a guardar
        """
        if not self.enable_cache or not explanation:
            return
        
        # Guardar en caché externo si está disponible
        if self._cache is not None:
            try:
                if hasattr(self._cache, "set"):
                    self._cache.set(cache_key, explanation, ttl=self.cache_ttl)
                    return
            except Exception as e:
                logger.warning(f"Failed to save to external cache: {e}")
        
        # Guardar en caché interno (FIFO simple, tamaño limitado)
        max_cache_size = 100
        if len(self._explanation_cache) >= max_cache_size:
            oldest_key = next(iter(self._explanation_cache))
            del self._explanation_cache[oldest_key]
        
        self._explanation_cache[cache_key] = explanation
    
    def _initialize(self) -> None:
        """
        Inicializar modelo y tokenizer de forma lazy.
        
        Raises:
            RuntimeError: Si hay error al cargar el modelo o tokenizer.
        """
        if self._initialized:
            return
        
        try:
            logger.info(f"Loading tokenizer for {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=True
            )
            
            logger.info(f"Loading model {self.model_name}...")
            model_kwargs: Dict[str, Any] = {
                "torch_dtype": torch.float16 if self.device.type == "cuda" else torch.float32,
                "low_cpu_mem_usage": True,
            }
            
            if self.device.type == "cuda":
                model_kwargs["device_map"] = "auto"
            
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            if self.device.type == "cpu":
                self.model = self.model.to(self.device)
            
            self.model.eval()
            
            # Optimizaciones si están disponibles
            if hasattr(torch, "compile") and self.device.type == "cuda":
                try:
                    self.model = torch.compile(self.model)
                    logger.info("Model compiled with torch.compile")
                except Exception as compile_error:
                    logger.warning(f"Could not compile model: {compile_error}")
            
            self._initialized = True
            
            num_params = sum(p.numel() for p in self.model.parameters())
            logger.info(
                f"CodeExplanationModel initialized - model: {self.model_name}, "
                f"device: {self.device}, params: {num_params:,}, "
                f"max_length: {self.max_length}, max_target_length: {self.max_target_length}"
            )
            
        except Exception as e:
            logger.error(f"Error initializing CodeExplanationModel: {e}", exc_info=True)
            self.model = None
            self.tokenizer = None
            self._initialized = False
            raise RuntimeError(f"Failed to initialize model: {e}") from e
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs: Any
    ) -> torch.Tensor:
        """
        Forward pass del modelo.
        
        Args:
            input_ids: Tensor con IDs de tokens de entrada.
            attention_mask: Máscara de atención opcional.
            **kwargs: Argumentos adicionales para el modelo.
        
        Returns:
            Tensor con las salidas del modelo.
        
        Raises:
            RuntimeError: Si el modelo no está inicializado.
        """
        if not self._initialized:
            self._initialize()
        
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        input_ids = input_ids.to(self.device)
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)
        
        return self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            **kwargs
        )
    
    def _generate_explanation(
        self,
        prompt: str,
        max_length: int,
        temperature: float,
        num_beams: int,
        do_sample: bool = True,
        **kwargs: Any
    ) -> str:
        """
        Generar explicación desde un prompt (método interno).
        
        Args:
            prompt: Prompt de entrada
            max_length: Longitud máxima
            temperature: Temperatura
            num_beams: Número de beams
            do_sample: Si usar sampling
            **kwargs: Argumentos adicionales
        
        Returns:
            Explicación generada
        """
        if not self._initialized:
            self._initialize()
        
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not initialized")
        
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
            padding=True
        ).to(self.device)
        
        generation_config = GenerationConfig(
            max_length=max_length,
            temperature=temperature,
            num_beams=num_beams if not do_sample else 1,
            do_sample=do_sample,
            early_stopping=True,
            pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            **kwargs
        )
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                generation_config=generation_config
            )
        
        explanation = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        ).strip()
        
        return explanation
    
    def generate(
        self,
        code: str,
        max_length: Optional[int] = None,
        temperature: float = 0.7,
        num_beams: int = 4,
        do_sample: bool = True,
        use_cache: Optional[bool] = None,
        **kwargs: Any
    ) -> str:
        """
        Generar explicación de código.
        
        Args:
            code: Código a explicar.
            max_length: Longitud máxima de la explicación (default: max_target_length).
            temperature: Temperatura para sampling (default: 0.7).
            num_beams: Número de beams para beam search (default: 4).
            do_sample: Si usar sampling (default: True).
            use_cache: Usar caché (default: self.enable_cache).
            **kwargs: Argumentos adicionales para generate().
        
        Returns:
            Explicación del código en lenguaje natural.
        
        Raises:
            RuntimeError: Si el modelo no está inicializado.
            ValueError: Si el código o parámetros son inválidos.
        """
        # Validar inputs
        code = self._validate_code(code)
        self._validate_generation_params(temperature, num_beams, max_length)
        
        self._stats["total_requests"] += 1
        use_cache = use_cache if use_cache is not None else self.enable_cache
        
        # Intentar obtener del caché
        if use_cache:
            cache_key = self._get_cache_key(
                code,
                max_length=max_length,
                temperature=temperature,
                num_beams=num_beams,
                do_sample=do_sample,
                **kwargs
            )
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for code explanation - key: {cache_key[:8]}")
                return cached_result
        
        # Generar explicación
        try:
            prompt = self.prompt_template.format(code=code)
            max_gen_length = max_length or self.max_target_length
            
            explanation = self._generate_explanation(
                prompt=prompt,
                max_length=max_gen_length,
                temperature=temperature,
                num_beams=num_beams,
                do_sample=do_sample,
                **kwargs
            )
            
            # Guardar en caché
            if use_cache:
                cache_key = self._get_cache_key(
                    code,
                    max_length=max_length,
                    temperature=temperature,
                    num_beams=num_beams,
                    do_sample=do_sample,
                    **kwargs
                )
                self._save_to_cache(cache_key, explanation)
            
            logger.debug(
                f"Code explanation generated - code_len: {len(code)}, "
                f"explanation_len: {len(explanation)}, max_length: {max_gen_length}"
            )
            
            return explanation
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Error generating explanation: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate explanation: {e}") from e
    
    def explain_code(
        self,
        code: str,
        language: Optional[str] = None,
        detail_level: str = "medium",
        **kwargs: Any
    ) -> str:
        """
        Explicar código con opciones adicionales.
        
        Args:
            code: Código a explicar.
            language: Lenguaje de programación (opcional).
            detail_level: Nivel de detalle ("brief", "medium", "detailed").
            **kwargs: Argumentos adicionales para generate().
        
        Returns:
            Explicación del código.
        
        Raises:
            ValueError: Si detail_level no es válido.
        """
        if detail_level not in self.PROMPT_TEMPLATES:
            raise ValueError(
                f"detail_level must be one of {list(self.PROMPT_TEMPLATES.keys())}, "
                f"got {detail_level}"
            )
        
        # Guardar template original
        original_template = self.prompt_template
        
        try:
            # Usar template según nivel de detalle
            language_str = language or "programming"
            self.prompt_template = self.PROMPT_TEMPLATES[detail_level].format(
                language=language_str,
                code="{code}"
            )
            
            # Ajustar max_length según nivel de detalle
            max_length_map = {
                "brief": self.max_target_length // 2,
                "medium": self.max_target_length,
                "detailed": self.max_target_length * 2
            }
            max_length = max_length_map.get(detail_level, self.max_target_length)
            
            return self.generate(code, max_length=max_length, **kwargs)
        finally:
            # Restaurar template original
            self.prompt_template = original_template
    
    def explain_batch(
        self,
        codes: List[str],
        max_length: Optional[int] = None,
        temperature: float = 0.7,
        num_beams: int = 4,
        do_sample: bool = True,
        **kwargs: Any
    ) -> List[str]:
        """
        Explicar múltiples códigos en batch (más eficiente).
        
        Args:
            codes: Lista de códigos a explicar.
            max_length: Longitud máxima de la explicación.
            temperature: Temperatura para sampling.
            num_beams: Número de beams para beam search.
            do_sample: Si usar sampling.
            **kwargs: Argumentos adicionales para generate().
        
        Returns:
            Lista de explicaciones en el mismo orden que los códigos.
        
        Raises:
            ValueError: Si codes está vacía o contiene elementos inválidos.
            RuntimeError: Si el modelo no está inicializado.
        """
        if not isinstance(codes, list):
            raise ValueError(f"codes must be a list, got {type(codes)}")
        
        if not codes:
            return []
        
        # Validar todos los códigos
        valid_codes: List[str] = []
        for i, code in enumerate(codes):
            try:
                valid_code = self._validate_code(code)
                valid_codes.append(valid_code)
            except ValueError as e:
                logger.warning(f"Skipping invalid code at index {i}: {e}")
        
        if not valid_codes:
            raise ValueError("No valid codes provided")
        
        # Validar parámetros
        self._validate_generation_params(temperature, num_beams, max_length)
        
        if not self._initialized:
            self._initialize()
        
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not initialized")
        
        try:
            # Construir prompts
            prompts = [self.prompt_template.format(code=code) for code in valid_codes]
            
            # Tokenizar batch
            inputs = self.tokenizer(
                prompts,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length,
                padding=True
            ).to(self.device)
            
            # Generar batch
            max_gen_length = max_length or self.max_target_length
            
            generation_config = GenerationConfig(
                max_length=max_gen_length,
                temperature=temperature,
                num_beams=num_beams if not do_sample else 1,
                do_sample=do_sample,
                early_stopping=True,
                pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                **kwargs
            )
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    generation_config=generation_config
                )
            
            # Decodificar batch
            explanations = [
                self.tokenizer.decode(output, skip_special_tokens=True).strip()
                for output in outputs
            ]
            
            # Guardar en caché
            if self.enable_cache:
                for code, explanation in zip(valid_codes, explanations):
                    if explanation:
                        cache_key = self._get_cache_key(
                            code,
                            max_length=max_length,
                            temperature=temperature,
                            num_beams=num_beams,
                            do_sample=do_sample,
                            **kwargs
                        )
                        self._save_to_cache(cache_key, explanation)
            
            avg_len = sum(len(e) for e in explanations) / len(explanations) if explanations else 0
            logger.debug(
                f"Batch code explanations generated - "
                f"batch_size: {len(valid_codes)}, avg_explanation_length: {avg_len:.1f}"
            )
            
            return explanations
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Error generating batch explanations: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate batch explanations: {e}") from e
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del modelo.
        
        Returns:
            Diccionario con estadísticas de uso.
        """
        total = self._stats["total_requests"]
        cache_hit_rate = (
            (self._stats["cache_hits"] / total * 100) if total > 0 else 0.0
        )
        
        return {
            **self._stats,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "initialized": self._initialized,
            "model_name": self.model_name,
            "device": str(self.device),
            "cache_enabled": self.enable_cache,
            "internal_cache_size": len(self._explanation_cache)
        }
    
    def clear_cache(self) -> int:
        """
        Limpiar caché de explicaciones.
        
        Returns:
            Número de entradas eliminadas.
        """
        count = 0
        
        # Limpiar caché externo
        if self._cache is not None:
            try:
                if hasattr(self._cache, "clear"):
                    self._cache.clear()
                    count += 1
                elif hasattr(self._cache, "delete_all"):
                    deleted = self._cache.delete_all()
                    count += deleted if isinstance(deleted, int) else 1
            except Exception as e:
                logger.warning(f"Error clearing external cache: {e}")
        
        # Limpiar caché interno
        count += len(self._explanation_cache)
        self._explanation_cache.clear()
        
        logger.debug(f"Cache cleared - {count} entries removed")
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del caché.
        
        Returns:
            Diccionario con estadísticas del caché.
        """
        return {
            "enabled": self.enable_cache,
            "external_cache_available": self._cache is not None,
            "internal_cache_size": len(self._explanation_cache),
            "internal_cache_max_size": 100,
            "cache_hits": self._stats["cache_hits"],
            "cache_misses": self._stats["cache_misses"],
            "cache_hit_rate": (
                (self._stats["cache_hits"] / (self._stats["cache_hits"] + self._stats["cache_misses"]) * 100)
                if (self._stats["cache_hits"] + self._stats["cache_misses"]) > 0 else 0.0
            )
        }
    
    def save(self, path: str) -> None:
        """
        Guardar modelo y tokenizer.
        
        Args:
            path: Ruta donde guardar el modelo.
        
        Raises:
            RuntimeError: Si el modelo no está inicializado.
        """
        if not self._initialized or self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not initialized")
        
        try:
            self.model.save_pretrained(path)
            self.tokenizer.save_pretrained(path)
            logger.info(f"CodeExplanationModel saved to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}", exc_info=True)
            raise RuntimeError(f"Failed to save model: {e}") from e
    
    @classmethod
    def load(
        cls,
        path: str,
        device: Optional[torch.device] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> "CodeExplanationModel":
        """
        Cargar modelo desde disco.
        
        Args:
            path: Ruta del modelo guardado.
            device: Dispositivo donde cargar el modelo (opcional).
            config: Configuración adicional (opcional).
        
        Returns:
            Instancia del modelo cargado.
        
        Raises:
            RuntimeError: Si hay error al cargar el modelo.
        """
        try:
            if config is None:
                config = {"model_name": path}
            else:
                config["model_name"] = path
            
            model = cls(config)
            if device:
                model.to_device(device)
            model._initialize()
            
            logger.info(f"CodeExplanationModel loaded from {path}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
            raise RuntimeError(f"Failed to load model: {e}") from e
