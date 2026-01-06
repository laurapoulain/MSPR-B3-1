@echo off
echo === Installation de NTL-SysToolbox (Windows) ===

:: Vérifie Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python non détecté. Installez Python 3 avant de continuer. https://www.python.org/downloads/windows/
    pause
    exit /b
)

:: Crée un environnement virtuel
echo === Creation de l'environnement ===
python -m venv venv_ntl

:: Active le venv
echo === Activation ===
call venv_ntl\Scripts\activate

:: Installe les dépendances
echo === Installation des dependances ===
pip install -r .requirements.txt

:: Lance le programme
echo === Lancement du programme ===
python Dev\main.py

echo === Fin de l'installation ===
pause
