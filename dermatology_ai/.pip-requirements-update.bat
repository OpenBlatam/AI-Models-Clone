@echo off
REM Script para actualizar y gestionar dependencias de Dermatology AI (Windows)

echo ==========================================
echo Dermatology AI - Dependency Manager
echo ==========================================

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help

if "%1"=="install" goto install_prod
if "%1"=="install-dev" goto install_dev
if "%1"=="install-min" goto install_min
if "%1"=="install-opt" goto install_opt
if "%1"=="update" goto update_deps
if "%1"=="outdated" goto show_outdated
if "%1"=="check" goto check_vulnerabilities
if "%1"=="compile" goto compile_lock
if "%1"=="clean" goto clean_cache
if "%1"=="size" goto show_size

echo Comando desconocido: %1
goto help

:install_prod
echo Instalando dependencias de produccion...
pip install -r requirements.txt
echo Instalacion completada
goto end

:install_dev
echo Instalando dependencias de desarrollo...
pip install -r requirements-dev.txt
echo Instalacion completada
goto end

:install_min
echo Instalando dependencias minimas...
pip install -r requirements-minimal.txt
echo Instalacion completada
goto end

:install_opt
echo Instalando dependencias optimizadas...
pip install -r requirements-optimized.txt
echo Instalacion completada
goto end

:update_deps
echo Actualizando dependencias...
pip list --outdated
goto end

:show_outdated
echo Dependencias desactualizadas:
pip list --outdated
goto end

:check_vulnerabilities
echo Verificando vulnerabilidades...
where safety >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo safety no esta instalado. Instalando...
    pip install safety
)
safety check -r requirements.txt
goto end

:compile_lock
echo Generando requirements-lock.txt...
where pip-compile >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalando pip-tools...
    pip install pip-tools
)
pip-compile requirements.txt -o requirements-lock.txt
echo requirements-lock.txt generado
goto end

:clean_cache
echo Limpiando cache de pip...
pip cache purge
echo Cache limpiado
goto end

:show_size
echo Tamaño estimado de dependencias:
echo.
echo requirements.txt:        ~2-3 GB
echo requirements-optimized.txt: ~500 MB
echo requirements-dev.txt:    ~3-4 GB
echo requirements-minimal.txt: ~50 MB
goto end

:help
echo Uso: %0 [comando]
echo.
echo Comandos disponibles:
echo   install          - Instalar dependencias de produccion
echo   install-dev      - Instalar dependencias de desarrollo
echo   install-min      - Instalar dependencias minimas
echo   install-opt      - Instalar dependencias optimizadas
echo   update           - Actualizar todas las dependencias
echo   outdated         - Mostrar dependencias desactualizadas
echo   check            - Verificar vulnerabilidades
echo   compile          - Generar requirements-lock.txt
echo   clean            - Limpiar cache de pip
echo   size             - Mostrar tamaño de dependencias
echo   help             - Mostrar esta ayuda
goto end

:end



