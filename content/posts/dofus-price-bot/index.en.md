---
title: "OCR Bot Dofus"
type: "posts"
author: WildPasta
published: 2024-03-01
description: "Automating Dofus crafting material cost"
summary: ""
draft: false
categories: ["application", "game"]
tags: ["bot", "python", "automation"]
---

## Intro

Like every two years, I fall back into a Dofus/Minecraft loop for about two months before quitting again.  
But this time, no more chasing Pious — it’s all about cost/yield calculation with Python!  
I decided to develop an auto-clicker to automatically fetch item prices from the in-game marketplace (HDV).

## The GUI

I had never touched **Tkinter** before, and now I know that building an application frontend with it is a **bad idea**.  
Still, I managed to put together an acceptable user interface:

{{< image src="images/dofus_cookbot_gui.png" alt="Cookbot GUI" caption="Cookbot GUI" >}}

You can select the items you want to craft to see the current prices of their ingredients in the marketplace.

## Recipes

The item recipes were retrieved directly from the [DofAPI crawler GitHub repo](https://github.com/dofapi/crawlit-dofus-encyclopedia-parser), which unfortunately is no longer maintained.  
They are presented as JSON dictionaries, which is how they are loaded into our tool.  
Here’s what a recipe looks like:

```json
{"_id": 14076,
"name": "Coiffe du Comte Harebourg",
"type": "Hat",
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

If a recipe is missing from the DofAPI database, we can fetch it manually using the API module and insert it into the `equipment_recipes.json` file.
We have a small utility that queries *dofusdb.fr* to retrieve the recipe.

Here’s an example:

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

I didn’t have the courage to dive into developing a MITM bot, so instead I used **Tesseract** for OCR (*Optical Character Recognition*) on in-game price screenshots.

When a recipe is loaded, `pyinput` automatically clicks the right search fields, fills in the item name, and captures the associated price in kamas (the unit price of the resource).
If Tesseract fails to recognize the price, it defaults to 1k and continues with the next search.

## The result

Once all the puzzle pieces are assembled, we can now calculate the price of our Royal Gobball Headgear without even opening a spreadsheet.

Here’s a demo running at 150% speed:

{{< gif src="images/dofus-cooker-demo.gif" alt="Cookbot Demo" caption="Cookbot Demo" >}}

And here’s what the terminal output looks like:

{{< image src="images/output_sample.png" alt="Cookbot Output Sample" caption="Cookbot Output Sample" >}}

## Improvements

I spent quite some time on this project, but there are still a few features that could improve accuracy.
For example, analyzing multi-buy prices could help determine if it’s cheaper to buy in bulk rather than individually.
Also, if two items share the same name but have different levels (yes, that happens ☠️), a click should be added to specify the desired item level.

Another issue with the auto-clicker is that it must be calibrated for your screen, so it clicks exactly on the right field and button.
I implemented a scaling function that adapts the positions proportionally to your screen size, but it’s not foolproof.
To help with this, I created a small `position_finder.py` utility, though some manual editing is still required.
Finally, analysis can only be performed on the computer’s main display.