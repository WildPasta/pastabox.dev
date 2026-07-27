---
title: "Generation of YouTube Shorts"
type: "posts"
author: WildPasta
published: 2023-06-08
description: "How to make money quickly with Python and a YouTube account"
draft: false
categories: ["application"]
tags: ["scraping", "python", "automation"]
---

## Intro

I recently came across YouTube channels dedicated to automated content creation using ChatGPT.
There's a real business built around this, with several tools created to "generate passive income" for you via TikTok or YouTube.
So I wanted to try the experience out by building my own bot.

## Downloading TikToks

Our best friend here will be the `BeautifulSoup` library, to parse the TikTok site.
I start by grabbing the URLs of popular TikToks from the platform's discover tab, keeping only videos with more than a million views.

```python
cookies, headers = load_tiktok_cookies()
response = requests.get(tiktok_url, headers=headers, cookies=cookies)

soup = BeautifulSoup(response.text, 'html.parser')
videos = soup.find_all('div', {'class': 'tiktok-1s72ajp-DivWrapper e1cg0wnj1'})
view_count = soup.find_all('div', {'class': 'tiktok-1md6snx-DivPlayContainer e19c29qe19'})
```

{{< admonition type=warning title="Damn web framework" open=true >}}
Note that this function breaks regularly, since TikTok's site classes change name fairly often (about once a month). It's probably possible to use XPath to handle this more dynamically — *I wasn't aware of that option at the time I built this*.
{{< /admonition >}}

The `ssstik.io` site is used to download the videos without a watermark, and they're stored on the host machine.
URLs, download dates, authors, and other info are saved in an SQLite database to avoid downloading the same video twice.
That same database will also be reused for uploading the videos to YouTube.

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

## Anti-Copyright (or not)

To avoid getting struck by YouTube, I tried setting up an *anticopyright* module, but I never managed to produce anything satisfying.
I did get to learn how to use the `moviepy` and `pydub` libraries to apply audio filters and video effects to the files, though.

## Uploading to YouTube

Uploading through an API key is **an absolute nightmare**.
You need to get your application verified by the platform to be able to publish videos publicly, and after trying to meet all the requirements three times, I gave up.

So I fell back on Selenium.
Big thanks to [ContentAutomation](https://github.com/ContentAutomation/YouTubeUploader) for their work: a ready-to-use Python module for uploading the videos you've downloaded!

I created a template for my video metadata, and built a function to give each video a random name.

```python
metadata_dict = {
    "title": title,
    "description": "Like and subscribe for more!",
    "category_id": 24,
    "tags": ["shorts", "trending", "viral", "tiktok"],
    "schedule": scheduled_date,
}
```

New YouTube accounts are limited in the number of videos they can publish per day during their first 6 months of existence.
So I had to schedule video uploads roughly every 5 days.