# Outil de labellisation

Outil permettant la classification et la labellisation de documents, ainsi que la correction du travail de l'OCR.


## Prise en main

EXECUTION :

avec l'ex�cutable :

    Cr�er l'ex�cutable avec '\builder\create_exe.bat'
    puis lancer '\dist\LabelTool\LabelTool.exe'

ou avec powerShell :

	  Lancer 'main.py' avec python



## Pr�requis

  avec l'ex�cutable :
  
    - PyInstaller
    
  ou avec PowerShell :
  
    - Python 3.7.3
    - Kivy 1.11.1
    - Pillow 6.0.0
  

## Installation

Pour cr�er l'ex�cutable :

PyInstaller:

    pip install pyInstaller

Pour lancer le main.py � la main avec PowerShell :

Python : 

    https://www.python.org/downloads/

Kivy : 

    python -m pip install --upgrade pip wheel setuptools virtualenv
    python -m pip install docutils pygments pypiwin32 kivy_deps.sdl2==0.1.22 kivy_deps.glew==0.1.12
    python -m pip install kivy_deps.gstreamer==0.1.17
    python -m pip install kivy_deps.angle==0.1.9
    python -m pip install kivy==1.11.1

    Puis dans kivy\uix\filechooser.py
    Ajoutez les lignes suivantes � la fonction scroll_to_top de la classe FileChooserListLayout :
      self.ids.scrollview.bar_width = 5
      self.ids.scrollview.scroll_type = ['bars']
    Cela rendra les bars de d�filement plus �paisse et plus facile � manier.
    Commenter les lignes 174 � 184 (contenu de la fonction is_hidden de la classe FileSystemLocal) si vous souhaitez
    cr�er l'ex�cutable.
    
Pillow:

    pip install Pillow
    

## Description du projet

### builder :

Permet la cr�ation de l'ex�cutable de l'outil de labellisation.

* create_exe.bat : script lan�ant la cr�ation de l'ex�cutable.

Note : la mani�re de cr�er l'ex�cutable pourrait �tre simplifi�e, mais ces instructions fonctionnent...

* LabelTool.spec : les sp�cifications n�cessaires � la cr�ation de l'ex�cutable.

### dist :

Dossier cr�� � l'issue du script create_exe.bat du dossier builder.
L'ex�cutable est : dist\LabelTool\LabelTool.exe

### doc :

Documentation d�veloppeur pour ex�cuter le code avec Python.

* README.md : documentation �ditable
* README.html : version HTML de la documentation

Note : Cette documentation contient les �tapes n�cessaires pour pouvoir lancer le code avec Python et y apporter des modifications.

### src :

* keyboard_icones : contient les images n�cessaires � l'interface graphique

* cancellation.py : impl�mentation du Ctrl+Z

* ColorWheel2.py : impl�mentation de la roue de couleur n�cessaire au choix des couleurs des labels

* data_description.py : contient les classes d�crivant diff�rentes structures de donn�es (les classes, les bo�tes, les pages et le document affich�)

* exceptions.py : contient les diff�rents types d'exceptions lev�es
* graphical_elements.py : contient diff�rentes classes d�crivant des objets graphiques de l'interface (ImageButton : les boutons-image sur lesquels on peut cliquer, comme les images des raccourcis, Token : les tokens affich�s dont on peu modifier la graphie, BIO_Label : les lettres de la labellisation B-I-O, Cursor : le curseur � l'�cran, BoxStencil : ce qui emp�che le visuel du document de d�passer sur les panneaux de contr�les lat�raux lorsqu'on le translate ou qu'on zoom)
* HelpDisplayer.py : impl�mentation de l'aide
* LinePlayground.py : Permet le dessin des rectangles pour l'utilisation des outils "Tag", "Create", "Merge", "Encapsulate", "Remove"
* LoadDialog.py : contenu (et non la Popup en elle-m�me) de la fen�tre de chargement des r�pertoires input dataset et output directory
* PieChart.py : impl�mentation du graphique circulaire
* popups.py : contient l'ensemble des Popups de l'interface
* Resizer.py : 
    * ResizableButton : bouton modifiable (bo�tes qu'on peut d�placer/redimensionner);
    * Resizer : classe qui g�re le d�placement et le redimensionnement des boutons modifiables, utilis�e lorsque l'utilisateur se sert de l'outil Move/Resize
* util.py : diverses fonctions pour calculer les positions relatives des bo�tes entre elles
* Zoom.py : objet graphique affichant l'image du document que l'on peu d�placer et sur lequel on peut zoomer
* gui.kv : fichier contenant une partie de la description de l'application utilis�e par le programme. Pour info un fichier .kv n'est pas n�cessaire pour construire une interface kivy, un .py est suffisant. Mais le .kv permet de d�crire certaines parties de l'interface de fa�on plus intuitive et les raccords (gestion des events, ajout de widget, acc�s aux attributs, .) entre le .kv et le .py sont simples � r�aliser; c'est un des avantages de Kivy.


## Remarques



## Auteur

Erwan Duvernay - Stagiaire R&D - AP

