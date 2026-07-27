---
title: "Switching from Medium to Github pages"
type: "posts"
author: WildPasta
published: 2026-07-27
description: "How to transfer content from Medium to Hugo on Github pages."
summary: ""
draft: false
categories: ["misc"]
---

## Intro
 
I went through a phase where I did several Sherlocks on HackTheBox, and I wanted somewhere to publish writeups for the *retired* challenges.
Writing a clean writeup already takes a fair bit of time, so it might as well be accessible and easy to update rather than left gathering dust somewhere.
For convenience, I chose to post them on Medium, but spoiler: it didn't end well, so I moved everything elsewhere.
 
## The Medium experience
 
No issues at first - sure, it lacked ergonomics for a few things (code blocks, spoilers, quotes...) - but writing on Medium was pretty intuitive, and publishing was hassle-free.
I went three months without a single issue, and then all of a sudden... Drama 💥
 
{{< image src="images/medium_email.png" alt="Email from Medium" caption="Email from Medium" >}}
 
I swear I thought I'd done things right by only posting content for writeups that had already been released, and I saw plenty of other HTB content on the platform.
 
No panic though - I'd already thought of a backup plan, I just hadn't gotten around to setting it up yet.
 
## The backup solution
 
I already had a blog running on Hugo, but I'd run into several headaches with Docker, since the image couldn't run on a Raspi (arm architecture).
So I decided to move everything to Github to stop dealing with that hassle and, as a side effect, hand over all intellectual property to Microsoft.
 
## Transferring the existing posts
 
I used an extension to convert all my existing Medium posts (by then set to restricted visibility by the admins) into Markdown, with the goal of posting them on a Hugo blog.
 
{{< image src="images/medium_to_markdown_extension.png" alt="Medium to Markdown extension" caption="Medium to Markdown extension" >}}
 
That said, I had to make several tweaks to the conversion (and so wrote a script to handle it).
 
First off, the images always pointed to `cdn-images-1.medium.com`, so I had to download every image from each post.
 
```python
def download_images(text: str, md_path: Path, images_dir: str = "images") -> str:
    """Download Medium-hosted images locally and rewrite links to local paths."""
    out_dir = md_path.parent / images_dir
    out_dir.mkdir(exist_ok=True)
 
    pattern = re.compile(r'!\[([^\]]*)\]\((https?://[^\s)]+)\)')
 
    def replace(match):
        alt, url = match.group(1), match.group(2)
        if "medium.com" not in url:
            return match.group(0)  # leave non-Medium images untouched
 
        ext = Path(urlparse(url).path).suffix or ".png"
        filename = re.sub(r'[^\w\-]', '_', alt)[:40] or "image"
        filename = f"{filename}_{abs(hash(url)) % 10000}{ext}"
        dest = out_dir / filename
 
        if not dest.exists():
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                dest.write_bytes(resp.content)
                print(f"Downloaded: {filename}")
            except requests.RequestException as e:
                print(f"Failed: {url} ({e})")
                return match.group(0)  # keep original link on failure
 
        return f"![{alt}]({images_dir}/{filename})"
 
    return pattern.sub(replace, text)
```
 
But once the images were downloaded, I didn't want a plain markdown image embed.
The DoIt theme offers a great shortcode for embedding an image with a caption in literally one tiny line.
So I wrote another regex to swap out the tags:
 
```python
def convert_images_to_shortcode(text: str) -> str:
    """Replace Markdown images with DoIt theme shortcodes."""
    image_pattern = re.compile(
        r'!\[(.*?)\]\((.*?)\)\s*\n_([^_]+)_',
        re.MULTILINE,
    )
 
    def replace_image(match):
        alt = match.group(1).strip().replace('"', "'")
        src = match.group(2).strip()
        caption = match.group(3).strip().replace('"', "'")
        return (
            '{{</* image '
            f'src="{src}" '
            f'alt="{alt}" '
            f'caption="{caption}" '
            '*/>}}'
        )
 
    return image_pattern.sub(replace_image, text)
```
 
Next, I wanted to convert the flag for each question into the ✨nice✨ DoIt theme callouts.
 
```python
def convert_flag_blocks(text: str) -> str:
    """Replace #flag code blocks with Hugo admonitions."""
    pattern = r"```(?:\w+)?\n#flag\n(.*?)\n```"
    replacement = (
        '{{</* admonition type="success" title="FLAG" open=true */>}}\n'
        r'\1'
        '\n{{</* /admonition */>}}'
    )
    return re.sub(pattern, replacement, text, flags=re.DOTALL)
```
 
And there you go, I'd managed to convert all my posts into ready-to-use Markdown.
 
## Automated publishing with Github Actions
 
Last step: all that was left was to automate publishing to Github Pages instead of rebuilding the site by hand for every new post.
A simple workflow is enough to build the Hugo site and deploy it to Github Pages on every push to `main`:
 
```yaml
name: Deploy Hugo site
 
on:
  push:
    branches: ["main"]
 
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: "latest"
          extended: true
      - run: hugo --minify
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```
 
No more building locally, no more trying to remember the command to run: just a `git push` and the site is up to date.
 
I also took the opportunity to update a few aging sections of my blog while I was at it, which certainly didn't hurt.
 
## Conclusion
 
In the end, this whole Medium mishap turned out to be a blessing in disguise: I now have a blog I control *almost* end to end.
Ideally I'd host it on my own VPS, but I'm saving that for whenever I get banned from Github over my writeups...