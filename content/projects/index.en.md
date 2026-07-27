---
title: "Projects"
type: "posts"
author: WildPasta
published: 2026-07-20
draft: false
hiddenFromHomePage: true
categories: ["projects"]
---

## 🏴‍☠️ Chall Maker 24HIUT

_**(March 2025 to June 2025)**_

I had the opportunity to contribute to one of [CTFER.io](https://github.com/ctfer-io) event by designing a series of CTF challenges for second-year computer science students.

Since the level was for second year students, we didn't have to pull out game breaking material.
In these circumstances, I managed to create **12 unique puzzles**.
I was focused on Forensic, Pentest and Web category.

The challenges I am most proud about are:
- [Turbo Timer](https://github.com/ctfer-io/24hiut2025/tree/main/challenges/misc/turbo-timer): alter game assets in a racing game to beat an impossible timer
- [Vault Dweller](https://github.com/ctfer-io/24hiut2025/tree/main/challenges/forensic/the-vault-dweller): analyse a memdump to reverse `vault.exe` binary and dump the flag from a **Notepad Tabstate** file

Beyond challenge development, I was also part of the on-site organization team in **Lyon**, where I helped manage the infrastructure and assisted participants by providing hints throughout the competition.

The CTF was powered by CTFER.io on-demand [chall-manager](https://github.com/ctfer-io/chall-manager), which dynamically deployed challenge instances and provided a highly available, seamless experience for all participants.

Full source is available [on Github](https://github.com/ctfer-io/24hiut2025).

## 🥚 Dofus Cooker

_**(July 2023)**_

After having fun playing Dofus, I wanted to use my programming skills to help me through some aspects of the game.
That's how this auto clicker bot was born.

Its goal is to compute the cost to craft an item to check if it's worth buying already made or not.
It helped me get a bunch of in-game money and ease my progression.

I wanted to do an entire MiTM bot but it was way too complex for me.
So instead I learned how to use Tesseract OCR and GUI in Python.

Source is available [on Github](https://github.com/WildPasta/dofus-price-bot).

## 💵 Tiktok to Youtube Shorts

_**(May 2023)**_

I wanted to make some money and got caught by the technical challenge instead of the potential profit.

That's how I built a bot that downloads trending Tiktok and uploads them on Youtube.
It applies a video and audio filter to avoid ban algorithm.

I learned a ton on official YouTube API (and unofficial ones), videos filters, automated web requests and creator side of YouTube Studio.

Source is private 😔

## 🎶 Youtube To MP3

_**(May 2023)**_

Bored of using ad-flooded web downloaders, I built my own self-hosted instance.

It uses Flask to expose the web GUI and Pytube to download the YT links.

Source is available [on Github](https://github.com/WildPasta/youtube_mp3_downloader).

## 🐴 Donk'LAN

_**(September 2022 to January 2023)**_

When setting up LAN parties with the e-sport association of my university, a tremendous amount of time was put into the preparation of network infrastructure and game servers.
So when we had the opportunity to choose our last year project, the team and I decided to develop a framework to **automate the whole infrastructure deployment**.

Donk'LAN is using **Packer**, **Terraform**, **Ansible** and **Nomad** to prepare a Proxmox server, setup the network and fire up the game servers.
The event we organized allowed us to stress test the process and improve it along the way.

It is fully modular and game templates already exists for: 
- Valheim
- Counter Strike
- Minecraft
- Teeworld

Donk'LAN uses network services such as: 
- Firewalling using pfSense
- Monitoring with Prometheus and Grafana
- Lancache
- Radius
- Traefik reverse proxy
- DNS
- Event web server

This ambitious project allowed us to shift our focus from managing infrastructure to creating better events, dramatically reducing setup time and operational overhead.

Source is available [on Github](https://github.com/donkesport/donk-lan).

## ⌚ Forensic on Smartwatches

_**(January 2022 to June 2022)**_

As part of a university project, I contributed to the development of a **digital forensics tool** for smartwatches.

The application enables investigators to connect a **Garmin** or **Samsung Galaxy Watch** and extract a wide range of forensic artifacts, providing valuable insights into the owner's activities.

Unlike traditional mobile forensic tools that focus on smartphones, this project **targets the smartwatch itself**, uncovering unique data that is only available from the wearable device.

To make the analysis process more accessible, the tool includes a **built-in web interface** that guides investigators through data extraction and presents the parsed information in a clear and organized way.

Some of the key features include retrieval of:
- GPS data and activity history
- Known SSIDs
- Personal files (contacts, calendar...)
- Application data (alarms, call logs, notifications...)
- System and device information

My main contribution focused on the **Garmin support**, where I designed and implemented the data acquisition and parsing components.

Source is private 😔

## 🤖 Discord Bots

Source code for all these bots is available on [Github](https://github.com/WildPasta?tab=repositories&q=discord)

### Birthday bot

Unambitious Discord bot built to never forget a birthday.
Create SQL database from JSON input.

### HFR Scraper

Custom scraper for hardware.fr built to search and receive alerts on specific keywords.
Supports search history to avoid getting spammed.

### Roasting Bot

Bot built to roast late student on the university Discord.
Includes a leaderboard for the best dunces.

## 🎄 Advent of Code

_**(December 2022)**_

I had fun solving some Advent of Code challenges and decided to share some solves on Github.

Source is available [on Github](https://github.com/WildPasta/advent_of_code).
