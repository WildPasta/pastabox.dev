---
title: "Web Scraping HFR"
type: "posts"
author: WildPasta
published: 2023-06-07
description: "Discord bot to scrap website"
draft: false
categories: ["application"]
tags: ["discord", "bot", "scraping", "python"]
---

## Intro

Some time ago, I was looking for a physical server to set up a Homelab.
I had already set up alerts on Leboncoin that I received on my phone, but I also wanted to get the listings from the [HFR forum](https://forum.hardware.fr/hfr/AchatsVentes/Hardware/liste_sujet-1.htm).
So, I started creating a Discord bot that now allows me to search from a dedicated channel.

## Discord Bot

The first step is to request a token from the [Discord Developer Portal](https://discord.com/developers/applications) to create your own bot.
It's a very easy process, and plenty of online resources will help you.

{{< admonition type=warning title="Keep your secret a secret" open=true >}}
Be careful to keep your token safe and revoke it if you suspect any compromise.
{{< /admonition >}}

For the bot to function properly, you also need to give it permission to read and send messages on the server where it is invited.

To create the search functionality, we use events from the `discord.py` library.
The user will need to call the bot with a command followed by a keyword to search.
Our bot will respond to messages starting with `!search`.

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

The `cooldown` function from the `discord.py` library limits the number of user requests to one every 10 seconds.
We will also limit the returns to 10 to avoid flooding the channel.

## Scraper HFR

To search for information on the HFR buying and selling forum, we will scrape the site using the `requests` library.
The forum pages that group the listings are in the form: `https://forum.hardware.fr/hfr/AchatsVentes/Hardware/liste_sujet-1.htm`.

{{< image src="images/site_web_hfr.png" alt="HFR marketplace forum" caption="HFR marketplace forum" >}}

We need to retrieve the content of the pages, iterate over them, and parse the HTML response from our requests (using `beautifulsoup`).
The elements we are interested in are the topics and the discussion links.

A topic is defined in a class `cCatTopic`, and we retrieve the content with the following snippet:

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

If the topic contains the keyword provided by the user, we return it with the corresponding link.
The link is found in the href from the beautifulsoup parsing (`cCatTopic["href"]`).

And there you have it, our automated tool to scrape HFR.

{{< image src="images/search_command_discord.png" alt="Result of search command" caption="Result of search command" >}}

## Notifications

In addition to this search function, I developed a script `new_alert.py` that will search for a keyword.
The goal is to call it every day with a cron job to send a message if a new item is found.

The cron looks like this:

```bash
00 10 * * * cd /home/bot && /usr/local/bin/python3 /home/bot/new_alert.py
```

{{< image src="images/notification_discord.png" alt="Discord alert" caption="Discord alert" >}}

The script behind it will work exactly like the search function but will not listen in a loop on Discord channels.
We also have a database (managed with `sqlite3`) to notify only when new listings are found.

## Download

The project is available on [Github](https://github.com/WildPasta/discord_bot_hfr_scraper).

The `README.md` makes it easy to get the project up and running.
A Docker container is even available to run it on your personal servers.