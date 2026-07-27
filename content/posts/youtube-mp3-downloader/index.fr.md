---
title: "Youtube MP3 Downloader"
type: "posts"
author: WildPasta
published: 2023-06-01
description: "Python Youtube MP3 Downloader"
draft: false
categories: ["application"]
tags: ["docker", "python"]
---

{{< admonition type=bug title="Bug actuel" open=true >}}
La librairie PyTube que j'utilisais renvoie maintenant une erreur 500 lors des téléchargements ([issue ouvert ici](https://github.com/WildPasta/youtube_mp3_downloader/issues/2)).
Le site Pytube.io est aussi devenu un site de paris en ligne 😔 Je pense que c'est la fin.
Je dois maintenant trouver le temps de réécrire le tout avec une nouvelle librairie.
{{< /admonition >}}

## Intro

J'avais besoin de récupérer l'audio de vidéos Youtube à partir d'un lien ou d'un fichier contenant des URLs à télécharger.

D'où mon envie de développer une application qui permettrait de se passer des sites type *youtube2mp3* comme le fameux **YouTube Converter**.

{{< image src="images/external_youtube_downloader.png" alt="Downloader Youtube externe" caption="Downloader Youtube externe" >}}

## L'application

Je voulais créer l'interface la plus minimaliste possible pour accéder directement aux fonctionnalités de l'application.
L'interface utilisateur est un serveur web Flask où il suffit de coller l'URL de la vidéo dont on veut télécharger l'audio.

{{< image src="images/youtube_downloader.png" alt="GUI web pour télécharger les fichiers MP3" caption="GUI web pour télécharger les fichiers MP3" >}}

Une fois l'interface terminée, il fallait créer le code qui télécharge les vidéos depuis Youtube.
J'utilise ici la librairie `pytube`, dédiée au téléchargement de vidéos Youtube.
Seul l'audio est téléchargé sur le serveur, puis on envoie le fichier `.mp3` au client.

Quelques mesures de sécurité basiques sont tout de même présentes.
Par exemple, on vérifie avec une expression régulière si l'URI fournie est bien une URL Youtube.
Le `mimetype` du fichier est aussi vérifié pour n'accepter que des fichiers audio.

Le stockage de la musique sur le serveur se fait dans un dossier `temp`, vidé dès qu'il dépasse 1 Go pour éviter toute surcharge d'espace disque.
Si une erreur est renvoyée pendant l'exécution, elle sera affichée sur la page web dans une section dédiée.

{{< image src="images/youtube_downloader_error.png" alt="Gestion des erreurs" caption="Gestion des erreurs" >}}

## Problème rencontré

Le seul vrai problème que j'ai rencontré pendant la création de cette application était l'écriture du fichier sur le serveur.
J'utilisais `AudioFileClip` de MoviePy pour écrire le fichier audio, et il était illisible.
Une façon plus propre et fonctionnelle que j'ai trouvée pour résoudre ce problème a été d'utiliser :

```python
    # Filter on audio track
    audio = youtube.streams.filter(only_audio=True).first()

    # Download audio file
    audio_file = audio.download(output_path=LOCAL_DOWNLOAD_FOLDER, filename=title)
    print(f"Audio file downloaded: {title}")
```

## Améliorations potentielles

Un mode sombre doit vraiment être ajouté à cette application pour éviter de se démolir les yeux.
Côté fonctionnel : pour une utilisation multi-client, il faut implémenter un téléchargement asynchrone ainsi qu'un mécanisme pour empêcher le nettoyage du dossier `temp` si un téléchargement est en cours.

## Téléchargement

L'application et toute sa documentation sont disponibles sur [Github](https://github.com/WildPasta/youtube_mp3_downloader).
