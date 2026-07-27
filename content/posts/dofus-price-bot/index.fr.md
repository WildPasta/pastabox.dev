---
title: "Autoclicker OCR sur Dofus"
type: "posts"
author: WildPasta
published: 2024-03-01
description: "Automatiser le calcul coût/rendement sur Dofus"
summary: ""
draft: false
categories: ["application", "game"]
tags: ["bot", "python", "automation"]
---

## Intro

Comme tous les deux ans, je retombe dans une boucle Dofus/Minecraft pour 2 mois avant de tout arrêter à nouveau.
Mais cette fois-ci, fini la chasse au piou et bonjour au calcul coût/rendement avec Python !
J'ai décidé de développer un auto-clicker pour récupérer le prix des objets en HDV.

## La GUI

Je n'avais jamais touché à **Tkinter** et je sais maintenant que faire du front applicatif avec cette librairie est une **mauvaise idée**.
J'ai quand même réussi à pondre une interface utilisateur acceptable.

{{< image src="images/dofus_cookbot_gui.png" alt="Cookbot GUI" caption="Cookbot GUI" >}}

On peut sélectionner les items que l'on veut confectionner pour voir le prix des matières premières en HDV.

## Les recettes

Les recettes des items ont été récupérées directement sur le Git du [crawler DofAPI](https://github.com/dofapi/crawlit-dofus-encyclopedia-parser) qui n'est malheureusement plus maintenu.
Elles sont présentées sous la forme d'un dictionnaire JSON et c'est ainsi qu'elles sont chargées dans notre outil.
Une recette ressemble à ça :

```json
{"_id": 14076,
"name": "Coiffe du Comte Harebourg",
"type": "Chapeau",
"lvl": "200",
"recipe": [{
        "Galet brasillant": {
            "id": "12740",
            "lvl": "150",
            "quantity": "3"
        }},{
        "Ethmoïde du Minotot": {
            "id": "13168",
            "lvl": "160",
            "quantity": "12"}}]}
```

Dans le cas où la recette n'est pas présente dans la base de DofAPI alors il faut aller la chercher avec le module API et l'insérer dans le fichier JSON `equipment_recipes.json`.
On a donc un utilitaire qui va aller taper l'API de *dofusdb.fr* pour récupérer sa recette.

Un exemple en image :

```powershell
> python3 .\api.py
Enter the name of the item: Dagues Hirr
Enter the level of the item: 197
[
{'name': 'Volve de Fistulor', 'quantity': 54, 'level': 170}, 
{'name': "Écorce d'Abrazif", 'quantity': 58, 'level': 170}, 
{'name': 'Pédoncule de Mérulette', 'quantity': 2, 'level': 170}, 
{'name': 'Patte de Korriandre', 'quantity': 2, 'level': 180}, 
{'name': 'Hamatum de Glourséleste', 'quantity': 1, 'level': 190}, 
{'name': 'Ardonite', 'quantity': 1, 'level': 200}, 
{'name': "Corne d'Ombre", 'quantity': 3, 'level': 190}, 
{'name': 'Trame Dimensionnelle', 'quantity': 12, 'level': 100}
]
```

## OCR

Je n'ai pas eu le courage de m'attaquer au développement d'un bot MiTM donc j'ai préféré utiliser Tesseract pour faire de l'OCR (*Optical character recognition*) sur les prix en kamas.

Lorsque la recette est chargée, `pyinput` va cliquer automatiquement sur les bons champs de recherche, remplir avec le nom de l'item et capturer le prix en kamas associé (prix unitaire de la ressource).
Si le prix n'est pas reconnu par Tesseract, il est mis à 1k et la recherche se poursuit.

## Le résultat


On met toute les pièces du puzzle ensemble, et voilà, on peut maintenant calculer le prix de notre Boufcoiffe Royale sans même avoir à sortir notre tableur Excel.

Ci-dessous une demo à vitesse 150% :

{{< gif src="images/dofus-cooker-demo.gif" alt="Cookbot Demo" caption="Cookbot Demo" >}}

La sortie dans notre terminal :

{{< image src="images/output_sample.png" alt="Sortie du script cookbot" caption="Sortie du script cookbot" >}}

## Les améliorations

J'ai passé pas mal de temps sur ce projets mais il reste quelques fonctionnalités à ajouter pour améliorer la précision.
Il faudrait notamment analyser le prix du multi-buy au cas où c'est plus avantageux d'acheter en lot plutôt qu'à l'unité.
Dans le cas où deux items porterait le même nom mais serait de niveau différents (oui ça existe ☠️) il faut ajouter un clic pour spécifier le niveau de l'objet.

Aussi le problème de l'autoclicker c'est qu'il faut calibrer son écran pour qu'il aille exactement sur le bon champ et clique sur le bon bouton.
J'ai mis en place une fonction qui s'adapte proportionnellement selon la taille de l'écran mais ce n'est pas infaillible.
Pour ça j'ai donc fait un petit `position_finder.py` mais il faut quand même aller modifier les valeurs en dur dans le code.
L'analyse ne peut aussi s'effectuer que sur l'écran principal du PC.
