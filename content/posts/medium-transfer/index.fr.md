---
title: "Passer de Medium aux Github Pages"
type: "posts"
author: WildPasta
published: 2026-07-27
description: "Comment je suis passé de Medium à Hugo sur Github."
summary: ""
draft: false
categories: ["misc"]
---

## Intro
 
J'ai eu un moment pendant lequel j'ai fait plusieurs Sherlock sur HackTheBox et je voulais un endroit où publier les writeups des challenges *retired*.
Rédiger un writeup propre demande déjà pas mal de temps, donc autant que ce soit accessible et facile à mettre à jour plutôt que de le laisser dormir dans un coin.
Par facilité j'ai choisi de les déposer sur Medium, mais spoiler : ça ne s'est pas bien fini, et j'ai donc tout transféré ailleurs.
 
## L'expérience sur Medium
 
Au début aucun souci, même si ça manquait d'ergonomie pour quelques trucs (code block, spoilers, citations...), la rédaction sur Medium était assez intuitive et la publication sans prise de tête.
J'ai passé trois mois sans aucun souci et puis d'un coup... Le drame 💥
 
{{< image src="images/medium_email.png" alt="Mail de Medium" caption="Mail de Medium" >}}
 
J'avoue que je pensais avoir bien fait les choses en postant uniquement du contenu dont les WU étaient déjà sortis, et je voyais beaucoup d'autre contenu HTB sur cette plateforme.
 
Pas de panique, j'avais déjà pensé à une solution de secours mais je n'avais pas encore pris le temps de la mettre en place.
 
## La solution de backup
 
J'avais déjà un blog qui tournait sur Hugo, mais j'avais rencontré plusieurs galères avec Docker, l'image ne pouvant pas tourner sur une Raspi (architecture arm).
J'ai donc décidé de tout passer sur Github pour ne plus me prendre la tête - et accessoirement céder toute propriété intellectuelle à Microsoft.
 
## Le transfert des posts existants
 
J'ai utilisé une extension pour convertir tous mes posts Medium existants - alors passés en visibilité restreinte par les modos - en Markdown, dans l'objectif de les poster sur un blog Hugo.
 
{{< image src="images/medium_to_markdown_extension.png" alt="Extension Medium to Markdown" caption="Extension Medium to Markdown" >}}
 
Cependant, j'ai dû apporter plusieurs modifications à la conversion (et donc écrire un script en conséquence).
 
Tout d'abord, les images pointaient toujours vers `cdn-images-1.medium.com`, donc je devais télécharger toutes les images de chaque post.
 
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
 
Sauf qu'une fois les images téléchargées, je ne voulais pas d'une simple intégration en markdown.
Le thème DoIt propose un super shortcode pour intégrer une image avec sa légende en littéralement une toute petite ligne.
J'ai donc refait une regex pour remplacer les balises :
 
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
 
Ensuite, je voulais convertir les flags de chaque question avec les ✨jolis✨ encarts du thème DoIt.
 
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
 
Et voilà, j'avais réussi à convertir mes posts en Markdown prêts à l'emploi.
 
## Publication automatique avec Github Actions
 
Pour finir, je n'avais plus qu'à automatiser la publication sur Github Pages plutôt que de rebuild le site à la main à chaque nouveau post.
Un simple workflow suffit à builder le site Hugo et à le déployer sur Github Pages à chaque push sur `main` :
 
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
 
Plus besoin de build en local, plus besoin de se souvenir de la commande à lancer : un simple `git push` et le site est à jour.
 
J'en ai également profité pour mettre un peu à jour certaines sections vieillissantes de mon blog, ce qui ne lui aura pas fait de mal.
 
## Conclusion
 
Au final cette mésaventure sur Medium aura été un mal pour un bien : j'ai maintenant un blog que je maîtrise *presque* de bout en bout.
L'idéal serait de l'héberger sur mon propre VPS mais je réserve ça pour le moment où je me ferais bannir de Github à cause des mes WU...
