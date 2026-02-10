# Pytest Cache

Este directorio contiene la caché de pytest para acelerar la ejecución de tests.

## ¿Qué es?

Pytest usa este directorio para almacenar información sobre:
- Tests ejecutados
- Resultados de tests
- Estado de fixtures
- Información de plugins

## ¿Debo versionarlo?

**No**, este directorio debe estar en `.gitignore` ya que es específico de cada máquina y puede regenerarse.

## Limpiar la caché

Si tienes problemas con tests, puedes limpiar la caché:

```bash
# Limpiar caché de pytest
pytest --cache-clear

# O eliminar manualmente
rm -rf .pytest_cache
```

## Beneficios

- Ejecución más rápida de tests
- Detección de tests que no han cambiado
- Mejor rendimiento en ejecuciones repetidas

