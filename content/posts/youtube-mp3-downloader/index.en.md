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

{{< admonition type=bug title="Current bug" open=true >}}
The PyTube library I was using now returns a 500 error when attempting downloads ([issue opened here](https://github.com/WildPasta/youtube_mp3_downloader/issues/2)).
Pytube.io site has also become an online gambling site 😔 I think this is the end.
I now must find the time to rewrite this with a new library.
{{< /admonition >}}

## Intro

I needed to download YouTube audio from a link or from a file containing URLs to download.

Hence my desire to develop an application that would eliminate the need for *youtube2mp3* type sites like the well-known **YouTube Converter**.

{{< image src="images/external_youtube_downloader.png" alt="Third party YouTube downloader" caption="Third party YouTube downloader" >}}

## The Application

I wanted to create the most minimalist interface possible to directly access the application's functionality.
The user interface is a Flask web server where you just have to paste the URL of the video whose audio you want to download.

{{< image src="images/youtube_downloader.png" alt="Simple web GUI to download MP3" caption="Simple web GUI to download MP3" >}}

Once the UI was completed, I needed to create the code that would download videos from YouTube.
Here I use the `pytube` library which is dedicated to downloading YouTube videos.
Only the audio is downloaded to the server, then we send the `.mp3` file to the client.

Some basic security measures are still present.
For example, we verify with a regular expression if the provided URI is indeed a YouTube URL.
The `mimetype` of the file is also checked to only accept audio files.

The storage of music on the server is done in a `temp` folder which is emptied as soon as it exceeds 1GB to avoid any disk space overload.
If an error is returned during execution, it will be displayed on the web page in a dedicated section.

{{< image src="images/youtube_downloader_error.png" alt="Error handling" caption="Error handling" >}}

## Problem Encountered

The only real problem I encountered during the creation of this application was writing the file on the server.
I was using MoviePy's `AudioFileClip` to write the audio file and it was unreadable.
A cleaner and functional way I found to solve this problem was to use:

```python
    # Filter on audio track
    audio = youtube.streams.filter(only_audio=True).first()

    # Download audio file
    audio_file = audio.download(output_path=LOCAL_DOWNLOAD_FOLDER, filename=title)
    print(f"Audio file downloaded: {title}")
```

## Potential Improvements

A dark mode really needs to be added to this application to avoid losing eyesight.
Functional side: for multi-client use, asynchronous downloading needs to be implemented and a process to prevent cleaning the `temp` folder if a download is in progress.

## Download

The application and all its documentation is available on [Github](https://github.com/WildPasta/youtube_mp3_downloader).