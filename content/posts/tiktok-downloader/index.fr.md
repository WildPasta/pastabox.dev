---
title: "Génération de shorts YouTube"
type: "posts"
author: WildPasta
published: 2023-06-08
description: "Comment se faire des sous rapidement avec Python et un compte YouTube"
draft: false
categories: ["application"]
tags: ["scraping", "python", "automation"]
---

## Intro

Je suis récemment tombé sur des chaînes YouTube dédiées à la création de contenu automatisé via ChatGPT.
Il y a un vrai business autour de ça, avec plusieurs outils créés pour vous "générer des revenus passifs" via TikTok ou YouTube.
J'ai donc voulu tenter l'expérience en développant mon propre bot.

## Téléchargement des TikTok

Notre meilleur ami ici sera la bibliothèque `BeautifulSoup`, pour parser le site TikTok.
Je commence par récupérer les URLs des TikToks populaires depuis l'onglet discover de la plateforme, en ne gardant que les vidéos ayant plus d'un million de vues.

```python
cookies, headers = load_tiktok_cookies()
response = requests.get(tiktok_url, headers=headers, cookies=cookies)

soup = BeautifulSoup(response.text, 'html.parser')
videos = soup.find_all('div', {'class': 'tiktok-1s72ajp-DivWrapper e1cg0wnj1'})
view_count = soup.find_all('div', {'class': 'tiktok-1md6snx-DivPlayContainer e19c29qe19'})
```

{{< admonition type=warning title="Foutu framework web" open=true >}}
Il faut noter que cette fonction plante régulièrement, car les classes du site TikTok changent de nom assez souvent (environ une fois par mois). Il est sûrement possible d'utiliser des XPath pour gérer ça plus dynamiquement — *je n'avais pas connaissance de cette possibilité au moment du développement*.
{{< /admonition >}}

Le site `ssstik.io` est utilisé pour télécharger les vidéos sans watermark, et celles-ci sont stockées sur la machine hôte.
Les URLs, dates de téléchargement, auteurs et d'autres informations sont enregistrées dans une base de données SQLite pour éviter de télécharger plusieurs fois la même vidéo.
Cette même base sera aussi réutilisée pour le téléversement des vidéos sur YouTube.

```python
def download_video(video_url: str, username: str, video_id: str) -> str:
    [...]
    response = requests.post('https://ssstik.io/abc', params=params, headers=headers, data=data, timeout=10)
    response.raise_for_status()
    downloadLink = BeautifulSoup(response.text, 'html.parser').a["href"]

    with requests.get(downloadLink, stream=True, headers=headers, timeout=10) as response:
        response.raise_for_status()
        filename = create_filename(username, video_id)

        with open("downloaded_videos/" + filename, "wb") as file:
            shutil.copyfileobj(response.raw, file)
    return filename

def download_workflow(videos, view_count):
    [...]
    for i, (video, count) in enumerate(zip(videos, view_count), 1):
        vc = count.strong.text
        if vc[-1] == 'M':
            video_url = video.a["href"]
            if not sql_tiktok_video_is_already_downloaded(video_url):
                username, video_id = extract_username_and_video_id(video_url)
                filename = download_video(video_url, username, video_id)
                if filename:
                    downloaded_videos.append(filename)
                    sql_tiktok_video_is_ready(filename, username, video_url)
                sleep(5)

    print(f'Successfully downloaded {len(downloaded_videos)} videos')
    return downloaded_videos
```

## Anti-Copyright (ou pas)

Pour éviter de me faire striker par YouTube, j'ai essayé de mettre en place un module *anticopyright*, mais je n'ai jamais réussi à sortir quelque chose de satisfaisant.
J'ai quand même pu apprendre à utiliser les librairies `moviepy` et `pydub` pour appliquer des filtres audio et des effets vidéo sur les fichiers.

## Mise en ligne sur YouTube

La mise en ligne via une clé d'API est **un véritable calvaire**.
Il faut faire vérifier son application par la plateforme pour pouvoir publier des vidéos en public, et après avoir essayé de remplir toutes les conditions à trois reprises, j'ai abandonné.

Je me suis donc rabattu sur Selenium.
Un grand merci à [ContentAutomation](https://github.com/ContentAutomation/YouTubeUploader) pour son travail : un module Python tout prêt à l'emploi pour uploader les vidéos qu'on a téléchargées !

J'ai créé un template pour mes métadonnées de vidéos, et développé une fonction pour donner des noms aléatoires à chaque vidéo.

```python
metadata_dict = {
    "title": title,
    "description": "Like and subscribe for more!",
    "category_id": 24,
    "tags": ["shorts", "trending", "viral", "tiktok"],
    "schedule": scheduled_date,
}
```

Les nouveaux comptes YouTube sont limités dans le nombre de vidéos publiées par jour pendant leurs 6 premiers mois d'existence.
J'étais donc contraint de programmer l'upload des vidéos tous les 5 jours environ.