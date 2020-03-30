# Outil de labellisation

Outil permettant la classification et la labellisation de documents, ainsi que la correction du travail de l'OCR.


## Prise en main

EXECUTION :

avec l'exécutable : (ne fonctionne pas)

    Placez vous dans le dossier 'builder\' puis lancez le script 'create_exe.bat' pour créer l'exécutable
    puis lancer 'dist\LabelTool\LabelTool.exe'

ou avec powerShell :

	  Lancer 'main.py' avec python

TESTER :

Une banque d'images ainsi que les boîtes OCR correspondantes sont données comme exemple dans le dossier 'dataset/' pour tester l'outil.
Lorsque l'application demande de sélectionner les 'input dataset' et 'output directory', veuillez entrer le chemin vers le dossier 'dataset/'.

## Prérequis

  avec l'exécutable : (ne fonctionne pas)
  
    - PyInstaller
    
  ou avec PowerShell :
  
    - Python 3.7.3
    - Kivy 1.11.1
    - Pillow 6.0.0
  

## Installation

Pour créer l'exécutable : (ne fonctionne pas)

PyInstaller:

    pip install pyInstaller==3.5

Pour lancer le main.py à la main avec PowerShell :

Python : 

    https://www.python.org/downloads/

Kivy : 
    python -m pip install setuptools==41.2.0 
    python -m pip install --upgrade pip wheel virtualenv
    python -m pip install docutils pygments pypiwin32 kivy_deps.sdl2==0.1.22 kivy_deps.glew==0.1.12
    python -m pip install kivy_deps.gstreamer==0.1.17
    python -m pip install kivy_deps.angle==0.1.9
    python -m pip install kivy==1.11.1

    Puis dans kivy\uix\filechooser.py
    Ajoutez les lignes suivantes à la fonction scroll_to_top de la classe FileChooserListLayout :
      self.ids.scrollview.bar_width = 5
      self.ids.scrollview.scroll_type = ['bars']
    Cela rendra les bars de défilement plus épaisse et plus facile à manier.
    Commenter les lignes 174 à 184 (contenu de la fonction is_hidden de la classe FileSystemLocal) si vous souhaitez
    créer l'exécutable.
    
Pillow:

    pip install Pillow==6.0.0
    

## Description du projet

### builder :

Permet la création de l'exécutable de l'outil de labellisation.

* create_exe.bat : script lançant la création de l'exécutable.

Note : la manière de créer l'exécutable pourrait être simplifiée, mais ces instructions fonctionnent...

* LabelTool.spec : les spécifications nécessaires à la création de l'exécutable.

### dist :

Dossier créé à l'issue du script create_exe.bat du dossier builder.
L'exécutable est : dist\LabelTool\LabelTool.exe

### doc :

Documentation développeur pour exécuter le code avec Python.

* README.md : documentation éditable
* README.html : version HTML de la documentation

Note : Cette documentation contient les étapes nécessaires pour pouvoir lancer le code avec Python et y apporter des modifications.

### src :

* keyboard_icones : contient les images nécessaires à l'interface graphique

* cancellation.py : implémentation du Ctrl+Z

* ColorWheel2.py : implémentation de la roue de couleur nécessaire au choix des couleurs des labels

* data_description.py : contient les classes décrivant différentes structures de données (les classes, les boîtes, les pages et le document affiché)

* exceptions.py : contient les différents types d'exceptions levées
* graphical_elements.py : contient différentes classes décrivant des objets graphiques de l'interface (ImageButton : les boutons-image sur lesquels on peut cliquer, comme les images des raccourcis, Token : les tokens affichés dont on peu modifier la graphie, BIO_Label : les lettres de la labellisation B-I-O, Cursor : le curseur à l'écran, BoxStencil : ce qui empêche le visuel du document de dépasser sur les panneaux de contrôles latéraux lorsqu'on le translate ou qu'on zoom)
* HelpDisplayer.py : implémentation de l'aide
* LinePlayground.py : Permet le dessin des rectangles pour l'utilisation des outils "Tag", "Create", "Merge", "Encapsulate", "Remove"
* LoadDialog.py : contenu (et non la Popup en elle-même) de la fenêtre de chargement des répertoires input dataset et output directory
* PieChart.py : implémentation du graphique circulaire
* popups.py : contient l'ensemble des Popups de l'interface
* Resizer.py : 
    * ResizableButton : bouton modifiable (boîtes qu'on peut déplacer/redimensionner);
    * Resizer : classe qui gère le déplacement et le redimensionnement des boutons modifiables, utilisée lorsque l'utilisateur se sert de l'outil Move/Resize
* util.py : diverses fonctions pour calculer les positions relatives des boîtes entre elles
* Zoom.py : objet graphique affichant l'image du document que l'on peu déplacer et sur lequel on peut zoomer
* gui.kv : fichier contenant une partie de la description de l'application utilisée par le programme. Pour info un fichier .kv n'est pas nécessaire pour construire une interface kivy, un .py est suffisant. Mais le .kv permet de décrire certaines parties de l'interface de façon plus intuitive et les raccords (gestion des events, ajout de widget, accès aux attributs, .) entre le .kv et le .py sont simples à réaliser; c'est un des avantages de Kivy.


## Remarques



## Auteur

Erwan Duvernay - Stagiaire R&D - AP

