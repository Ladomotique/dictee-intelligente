# 🎙️ Dictée Intelligente (Mistral Voxtral)

Une application bureau moderne, rapide et élégante pour la dictée vocale, propulsée par l'API audio **Mistral**.
Transformez votre voix en texte instantanément : l'application tape le texte automatiquement à l'endroit exact où se trouve votre curseur (que vous soyez sur Word, votre navigateur ou un éditeur de code) !

## 🌟 Fonctionnalités Principales

* **Deux modes d'utilisation intuitifs** :
  * **Mode Interface** : Cliquez sur le grand bouton central pour lancer l'enregistrement, avec affichage d'un minuteur en temps réel, puis cliquez à nouveau pour l'arrêter.
  * **Mode Raccourci Global (Alt+W)** : Maintenez `Alt+W` enfoncé depuis n'importe quelle application pour dicter, relâchez la touche pour arrêter et transcrire le texte.
* **Historique des transcriptions** : L'interface conserve vos 10 dernières dictées. Chaque élément dispose d'un bouton de copie rapide ("📋") pour récupérer vos textes sans effort.
* **Mode Compact** : Réduisez la fenêtre à un minuscule widget flottant pour garder l'essentiel visible sans gêner votre espace de travail.
* **Feedback Audio Personnalisable** : 10 profils sonores distincts configurables pour vous confirmer auditivement le début et la fin de la prise de son.
* **Design Moderne** : Thème sombre, épuré et professionnel généré sous `CustomTkinter`.

## ⚙️ Prérequis & Lancement

L'application est conçue pour fonctionner de manière autonome.

### 🔌 Option 1 : Utilisation des exécutables (Aucune installation Python requise)
L'application peut être compilée en exécutable autonome via PyInstaller.
1. Allez dans le dossier `dist/` (si disponible via les versions ou généré localement).
2. Lancez `DicteeVocale.exe` sous Windows. Vous pouvez déplacer ce fichier où vous voulez !
*(Pour Mac, utilisez le script libre `build_mac.sh` sur un environnement macOS).*

### 🐍 Option 2 : Lancement via le code source
Si vous souhaitez exécuter ou modifier le script source :
1. Assurez-vous d'avoir Python installé et vos pilotes audio fonctionnels.
2. Ouvrez un terminal dans le dossier du projet.
3. Installez les librairies requises : `pip install -r requirements.txt`
4. Lancez l'application : `python app.py` (ou double-cliquez sur `lancer_dictee.bat` sous Windows).

## 🔐 Configuration (Clé API Mistral)

L'application utilise le moteur vocal en ligne de **Mistral API** pour traduire le son en texte. **Par conséquent, vous devez obligatoirement fournir votre propre clé API Mistral.**

1. Lancez l'application.
2. Cliquez sur l'icône des **Paramètres (⚙️)** en haut à droite de la fenêtre.
3. Insérez votre clé API secrète dans le champ dédié.
4. Cliquez sur **Sauvegarder**. (La configuration est sécurisée localement dans un fichier `config.json`).

Vous êtes maintenant prêt à dicter ! 🎤
