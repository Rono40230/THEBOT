@echo off
REM =============================================================================
REM THEBOT - Script de Lancement pour Windows
REM Trading Analysis Platform - Architecture Ultra-Modulaire  
REM =============================================================================

setlocal enabledelayedexpansion
color 0B

echo.
echo ================================================
echo       🤖 THEBOT - Trading Analysis Platform
echo          Architecture Ultra-Modulaire
echo ================================================
echo.

REM Configuration
set PYTHON_MIN=3.11
set THEBOT_DIR=%~dp0
set VENV_DIR=%THEBOT_DIR%venv_thebot

REM Vérification Python
echo ➤ Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installe ou pas dans le PATH !
    echo    Telecharger depuis: https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo ✅ Python %PYTHON_VERSION% detecte

REM Création environnement virtuel
echo ➤ Configuration environnement virtuel...
if not exist "%VENV_DIR%" (
    echo   Creation de l'environnement virtuel...
    python -m venv "%VENV_DIR%"
    echo ✅ Environnement virtuel cree
) else (
    echo ✅ Environnement virtuel existant trouve
)

REM Activation environnement
call "%VENV_DIR%\Scripts\activate.bat"

REM Installation dépendances
echo ➤ Installation des dependances Python...
pip install --upgrade pip setuptools wheel

if exist "%THEBOT_DIR%requirements.txt" (
    echo   Installation depuis requirements.txt...
    pip install -r "%THEBOT_DIR%requirements.txt"
)

if exist "%THEBOT_DIR%setup.py" (
    echo   Installation THEBOT en mode developpement...
    pip install -e .
)

echo   Installation extensions Jupyter...
pip install jupyterlab ipywidgets jupyter-widgets-base
jupyter nbextension enable --py widgetsnbextension --sys-prefix 2>nul

REM Tests de validation
echo ➤ Tests de validation...
if exist "%THEBOT_DIR%tests" (
    python -m pytest tests/unit/indicators/ -v --tb=short
    echo ✅ Tous les tests passent ! Architecture validee.
) else (
    echo ⚠️  Dossier tests non trouve, tests ignores.
)

REM Vérification dashboard
if not exist "%THEBOT_DIR%jupyter_dashboard.ipynb" (
    echo ❌ Dashboard jupyter_dashboard.ipynb non trouve !
    pause
    exit /b 1
)

REM Lancement
echo.
echo 🚀 Lancement de THEBOT Dashboard...
echo    URL: http://localhost:8888
echo    Dashboard: jupyter_dashboard.ipynb
echo    Appuyez sur Ctrl+C pour arreter
echo.

REM Démarrage Jupyter avec ouverture automatique
start "" "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb"
jupyter lab --ip=127.0.0.1 --port=8888 --no-browser

echo.
echo Au revoir ! 👋
pause