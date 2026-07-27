---
title: "Web Scraping HFR"
type: "posts"
author: WildPasta
published: 2023-06-07
description: "Bot Discord pour scraper un site web"
draft: false
categories: ["application"]
tags: ["discord", "bot", "scraping", "python"]
---

## Intro

Il y a quelque temps, je cherchais un serveur physique pour monter un Homelab.
J'avais déjà mis en place des alertes sur Leboncoin que je recevais sur mon téléphone, mais je voulais aussi récupérer les annonces du [forum HFR](https://forum.hardware.fr/hfr/AchatsVentes/Hardware/liste_sujet-1.htm).
Alors, j'ai créé un bot Discord qui me permet maintenant de chercher depuis un channel Discord dédié.

## Bot Discord

La première étape est de demander un token sur le [Discord Developer Portal](https://discord.com/developers/applications) pour créer son propre bot.
C'est une démarche vraiment simple, et plein de ressources en ligne sont disponibles.

{{< admonition type=warning title="Un secret, ça reste secret" open=true >}}
Attention à bien garder le token en sécurité et à le révoquer s'il est compromis.
{{< /admonition >}}

Pour que le bot fonctionne correctement, il faut aussi lui donner la permission de lire et d'envoyer des messages sur le serveur où il est invité.

Pour créer la fonctionnalité de recherche, on utilise des events de la librairie `discord.py`.
L'utilisateur devra appeler le bot avec une commande suivie d'un mot-clé à rechercher.
Notre bot répondra aux messages commençant par `!search`.

```python
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
[...]
@bot.command(name="search")
[...]
async def search(ctx, *keywords):
    search_query = " ".join(keywords)
    ads_dict = get_ads(DEEP, search_query)
    [...]
    embed = discord.Embed(title=f"Search for '{search_query}':")
    for url, title in ads_dict.items():
        embed.add_field(name=title, value=url, inline=False)
    [...]
    await ctx.send(embed=embed)
```

La fonction `cooldown` de la librairie `discord.py` limite le nombre de requêtes utilisateur à une toutes les 10 secondes.
On va aussi limiter les retours à 10 pour éviter de spammer le salon.

## Scraper HFR

Pour chercher des infos sur le forum d'achat-vente HFR, on va scraper le site avec la librairie `requests`.
Les pages du forum qui regroupent les annonces sont de la forme : `https://forum.hardware.fr/hfr/AchatsVentes/Hardware/liste_sujet-1.htm`.

{{< image src="images/site_web_hfr.png" alt="Marketplace du forum HFR" caption="Marketplace du forum HFR" >}}

Il faut récupérer le contenu des pages, itérer dessus, et parser la réponse HTML de nos requêtes (avec `beautifulsoup`).
Les éléments qui nous intéressent sont les sujets et les liens de discussion.

Un sujet est défini dans une classe `cCatTopic`, et on récupère le contenu avec le snippet suivant :

```python
# We will fetch the content of the pages
for i in range(deep):
    url = f"https://forum.hardware.fr/hfr/AchatsVentes/Hardware/liste_sujet-{i}.htm"
    response = requests.get(url)

# We parse the topics with beautifulsoup
soup = BeautifulSoup(response.content, 'html.parser')
ads = soup.find_all("td", {"class": "sujetCase3"})
for ad in ads:
    cCatTopic = ad.find("a", {"class": "cCatTopic"})
```

Si le sujet contient le mot-clé fourni par l'utilisateur, on le renvoie avec le lien correspondant.
Le lien se trouve dans le href récupéré par le parsing beautifulsoup (`cCatTopic["href"]`).

Et voilà, notre outil automatisé pour scraper HFR.

{{< image src="images/search_command_discord.png" alt="Résultat de la commande search" caption="Résultat de la commande search" >}}

## Notifications

En plus de cette fonction de recherche, j'ai développé un script `new_alert.py` qui va chercher un mot-clé.
Le but est de l'appeler tous les jours avec un cron job pour envoyer un message si une nouvelle annonce est trouvée.

Le cron ressemble à ça :

```bash
00 10 * * * cd /home/bot && /usr/local/bin/python3 /home/bot/new_alert.py
```

{{< image src="images/notification_discord.png" alt="Alerte Discord" caption="Alerte Discord" >}}

Le script derrière fonctionne exactement comme la fonction de recherche, mais n'écoute pas en boucle sur les salons Discord.
On a aussi une base de données (gérée avec `sqlite3`) pour notifier uniquement quand de nouvelles annonces sont trouvées.

## Téléchargement

Le projet est disponible sur [Github](https://github.com/WildPasta/discord_bot_hfr_scraper).

Le `README.md` permet de lancer facilement le projet.
Un conteneur Docker est même disponible pour le faire tourner sur un serveur perso.