#!/bin/bash
# Script de compilation pour macOS
# Assurez-vous d'avoir Python et PyInstaller installés : pip install pyinstaller

echo "Création de l'application macOS de la Dictée Vocale Mistral..."
pyinstaller --noconsole --onefile --windowed --name "DicteeVocale" app.py
echo "Terminé ! L'application se trouve dans le dossier 'dist/'."
