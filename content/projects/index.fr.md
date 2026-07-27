---
title: "Projets"
type: "posts"
author: WildPasta
published: 2026-07-20
draft: false
hiddenFromHomePage: true
categories: ["projects"]
---

## 🏴‍☠️ Chall Maker 24HIUT

_**(Mars 2025 à Juin 2025)**_

J'ai eu l'opportunité de contribuer à un événement de [CTFER.io](https://github.com/ctfer-io) en concevant une série de challenges CTF pour des étudiants de deuxième année en informatique.

Vu que le niveau visait des étudiants de deuxième année, j'ai fais des challenges abordables en terme de difficulté -et aussi parce que je n'aurais pas été capable de faire plus dur.
J'ai donc créé **12 challenges** et participé au test des 22 autres.
Je me suis concentré sur les catégories Forensic, Pentest et Web.

Les challenges dont je suis le plus fier sont :
- [Turbo Timer](https://github.com/ctfer-io/24hiut2025/tree/main/challenges/misc/turbo-timer) : modifier les assets d'un jeu de course pour battre un chrono impossible
- [Vault Dweller](https://github.com/ctfer-io/24hiut2025/tree/main/challenges/forensic/the-vault-dweller) : analyser un memdump pour reverse le binaire `vault.exe` et récupérer le flag depuis un fichier Notepad Tabstate

En plus de la création des challenges, j'ai aussi fait partie de l'équipe d'organisation sur place à **Lyon**, où j'ai aidé à gérer l'infrastructure et donné tips aux participants tout au long de la compétition.

Le CTF tournait sur la stack [chall-manager](https://github.com/ctfer-io/chall-manager) de CTFER.io, qui déployait dynamiquement les instances de challenges et garantissait une expérience fluide et hautement disponible pour tous les participants.

Code source disponible [sur Github](https://github.com/ctfer-io/24hiut2025).

## 🥚 Dofus Cooker

_**(Juillet 2023)**_

Après m'être bien amusé sur Dofus, j'ai voulu utiliser mes compétences en programmation pour m'aider sur certains aspects du jeu.
C'est comme ça qu'est né ce bot auto-clicker.

Son but est de calculer le coût de fabrication d'un objet pour vérifier s'il vaut mieux l'acheter déjà fait ou non.
Ça m'a aidé à accumuler pas mal d'argent en jeu et à accélérer ma progression.

Je voulais faire un bot MiTM complet mais c'était bien trop complexe pour moi.
Du coup, j'ai plutôt appris à utiliser Tesseract OCR et les interfaces graphiques en Python.

Code source disponible [sur Github](https://github.com/WildPasta/dofus-price-bot).

## 💵 Tiktok to Youtube Shorts

_**(Mai 2023)**_

Je voulais me faire un peu d'argent, mais je me suis laissé happer par le défi technique plutôt que par le profit potentiel.

C'est comme ça que j'ai construit un bot qui télécharge les Tiktoks tendance et les upload sur Youtube.
Il applique un filtre vidéo et audio pour éviter l'algorithme de bannissement.

J'ai appris un max sur l'API officielle de YouTube (et les non-officielles), les filtres vidéo, les requêtes web automatisées et le côté créateur de YouTube Studio.

Code source privé 😔

## 🎶 Youtube To MP3

_**(Mai 2023)**_

Fatigué des downloaders web bourrés de pubs, j'ai monté ma propre instance self-hosted.

Elle utilise Flask pour exposer l'interface web et Pytube pour télécharger les liens YT.

Code source disponible [sur Github](https://github.com/WildPasta/youtube_mp3_downloader).

## 🐴 Donk'LAN

_**(Septembre 2022 à Janvier 2023)**_

En organisant des LAN avec l'association e-sport de mon université, on passait un temps monstre à préparer l'infrastructure réseau et les serveurs de jeu.
Alors quand on a eu l'occasion de choisir notre projet de dernière année, l'équipe et moi avons décidé de développer un framework pour **automatiser entièrement le déploiement de l'infrastructure**.

Donk'LAN utilise **Packer**, **Terraform**, **Ansible** et **Nomad** pour préparer un serveur Proxmox, configurer le réseau et lancer les serveurs de jeu.
L'événement qu'on a organisé nous a permis de stress-tester le processus et de l'améliorer au fil du temps.

Il est entièrement modulaire et des templates de jeu existent déjà pour :
- Valheim
- Counter Strike
- Minecraft
- Teeworld

Donk'LAN utilise des services réseau tels que :
- Pare-feu avec pfSense
- Monitoring avec Prometheus et Grafana
- Lancache
- Radius
- Reverse proxy Traefik
- DNS
- Serveur web de l'événement

Ce projet ambitieux nous a permis de passer de la gestion d'infrastructure à la création de meilleurs événements, en réduisant drastiquement le temps de préparation et la charge opérationnelle.

Code source disponible [sur Github](https://github.com/donkesport/donk-lan).

## ⌚ Forensic on Smartwatches

_**(Janvier 2022 à Juin 2022)**_

Dans le cadre d'un projet universitaire, j'ai contribué au développement d'un **outil de forensic numérique** pour montres connectées.

L'application permet aux investigateurs de connecter une **Garmin** ou une **Samsung Galaxy Watch** et d'extraire un large éventail d'artefacts forensiques, offrant des informations sur les activités du propriétaire.

Contrairement aux outils de forensic mobile traditionnels centrés sur les smartphones, ce projet **cible directement la montre connectée**, révélant des données uniques uniquement disponibles depuis l'appareil porté.

Pour rendre le processus d'analyse plus accessible, l'outil inclut une **interface web intégrée** qui guide les enquêteurs à travers l'extraction des données et présente les informations traitées de façon claire et organisée.

Parmi les fonctionnalités clés, on retrouve la récupération de :
- Données GPS et historique d'activité
- SSIDs connus
- Fichiers personnels (contacts, calendrier...)
- Données d'application (alarmes, journaux d'appels, notifications...)
- Informations système et appareil

Ma contribution principale s'est concentrée sur **l'intégration Garmin**, où j'ai conçu et implémenté les composants d'acquisition et de traitement des données.

Code source privé 😔

## 🤖 Discord Bots

Le code source de tous ces bots est disponible sur [Github](https://github.com/WildPasta?tab=repositories&q=discord)

### Birthday bot

Bot Discord sans prétention conçu pour ne jamais oublier un anniversaire.
Crée une base de données SQL à partir d'une entrée JSON.

### HFR Scraper

Scraper personnalisé pour hardware.fr conçu pour rechercher des mots-clés spécifiques et recevoir des alertes.
Prend en charge un historique de recherche pour éviter de se faire spammer.

### Roasting Bot

Bot conçu pour clasher les étudiants en retard sur le Discord de l'université.
Inclut un classement des meilleurs cancres.

## 🎄 Advent of Code

_**(Décembre 2022)**_

Je me suis amusé à résoudre des challenges de l'Advent of Code et j'ai décidé de partager quelques solutions sur Github.

Le code source est disponible [sur Github](https://github.com/WildPasta/advent_of_code).
