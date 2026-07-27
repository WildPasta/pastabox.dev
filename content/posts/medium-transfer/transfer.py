import re
import sys
from pathlib import Path
from urllib.parse import urlparse
import requests


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


def convert_flag_blocks(text: str) -> str:
    """Replace #flag code blocks with Hugo admonitions."""
    pattern = r"```(?:\w+)?\n#flag\n(.*?)\n```"
    replacement = (
        '{{< admonition type=success title="FLAG" open=false >}}\n'
        r'\1'
        '\n{{< /admonition >}}'
    )
    return re.sub(pattern, replacement, text, flags=re.DOTALL)


def add_task_spacing(text: str) -> str:
    """Insert vertical spacing before each task heading."""
    return re.sub(
        r'^(>\s*Task\s+\d+:)',
        '{{< style "height:2rem;" >}}{{< /style >}}\n\\1',
        text,
        flags=re.MULTILINE,
    )


def convert_images_to_shortcode(text: str) -> str:
    """Replace Markdown images (with an italic caption line below) with Hugo image shortcodes."""
    image_pattern = re.compile(
        r'!\[(.*?)\]\((.*?)\)\s*\n_([^_]+)_',
        re.MULTILINE,
    )

    def replace_image(match):
        alt = match.group(1).strip()
        src = match.group(2).strip()
        caption = match.group(3).strip()
        return (
            '{{< image '
            f'src="{src}" '
            f'alt="{alt}" '
            f'caption="{caption}" '
            '>}}'
        )

    return image_pattern.sub(replace_image, text)


def process(md_path: str, images_dir: str = "images"):
    md_path = Path(md_path)
    text = md_path.read_text(encoding="utf-8")

    text = download_images(text, md_path, images_dir)
    text = convert_flag_blocks(text)
    text = add_task_spacing(text)
    text = convert_images_to_shortcode(text)

    md_path.write_text(text, encoding="utf-8")
    print(f"Done. Updated {md_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process.py <path-to-markdown-file> [images-dir]")
        sys.exit(1)

    images_dir = sys.argv[2] if len(sys.argv) > 2 else "images"
    process(sys.argv[1], images_dir)