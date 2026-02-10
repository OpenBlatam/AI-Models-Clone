@echo off
REM MOEA Quick Commands - Script de comandos rápidos para Windows
REM Uso: moea_quick_commands.bat [comando]

if "%1"=="" (
    echo MOEA Quick Commands
    echo.
    echo Comandos disponibles:
    echo   gen       - Generar proyecto
    echo   setup     - Configurar proyecto
    echo   test      - Probar API
    echo   monitor   - Monitorear sistema
    echo   dash      - Dashboard web
    echo   health    - Health check
    echo   backup    - Crear backup
    echo   clean     - Limpieza
    echo   analytics - Análisis
    echo   security  - Auditoría de seguridad
    echo   docs      - Generar documentación
    echo   perf      - Performance
    echo   ai        - Asistente IA
    echo   full-setup - Setup completo
    echo   full-test  - Tests completos
    echo   daily      - Tareas diarias
    goto :end
)

if "%1"=="gen" python quick_moea.py & goto :end
if "%1"=="setup" python moea_setup.py & goto :end
if "%1"=="test" python moea_test_api.py & goto :end
if "%1"=="monitor" python moea_monitor.py & goto :end
if "%1"=="dash" python moea_dashboard.py & goto :end
if "%1"=="health" python moea_health.py & goto :end
if "%1"=="backup" python moea_backup.py create generated_projects/moea_optimization_system & goto :end
if "%1"=="clean" python moea_cleanup.py --all & goto :end
if "%1"=="analytics" python moea_analytics.py --report analytics.json & goto :end
if "%1"=="security" python moea_security.py generated_projects/moea_optimization_system & goto :end
if "%1"=="docs" python moea_docs.py generated_projects/moea_optimization_system & goto :end
if "%1"=="perf" python moea_performance.py --report performance.json & goto :end
if "%1"=="ai" python moea_ai_assistant.py --interactive & goto :end

if "%1"=="full-setup" (
    echo 🚀 MOEA Full Setup
    python quick_moea.py
    python moea_setup.py
    python verify_moea_project.py
    python moea_health.py
    goto :end
)

if "%1"=="full-test" (
    echo 🧪 MOEA Full Test Suite
    python moea_health.py
    python moea_test_api.py
    python moea_security.py generated_projects/moea_optimization_system
    python moea_performance.py --report test_performance.json
    goto :end
)

if "%1"=="daily" (
    echo 📊 MOEA Daily Tasks
    python moea_analytics.py --report daily_analytics.json
    python moea_cleanup.py --all
    python moea_backup.py create generated_projects/moea_optimization_system
    goto :end
)

echo ❌ Comando no reconocido: %1
echo Usa sin argumentos para ver ayuda

:end

