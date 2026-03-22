@echo off
echo Lancement de l'application de dictee vocale...
python app.py
if %errorlevel% neq 0 (
    echo.
    echo Une erreur est survenue ! Lisez le message ci-dessus pour comprendre le probleme.
    pause
) else (
    echo Application fermee.
)
