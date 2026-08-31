import shutil
from pathlib import Path

import marko
import yaml
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup


def build() -> None:
    root = Path(__file__).resolve().parent.parent
    data_dir = root / "data"
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)

    env = Environment(loader=FileSystemLoader(root / "templates"))
    env.filters["markdown"] = lambda t: Markup(marko.Markdown(extensions=["gfm"]).convert(t))

    for locale in sorted(p.name for p in data_dir.iterdir() if p.is_dir()):
        with open(data_dir / locale / "main.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        other_locales = sorted(x.name for x in data_dir.iterdir() if x.is_dir() and x.name != locale)
        html = env.get_template("main.html").render(data, other_locales=other_locales, lang=locale)
        out = output_dir / "index.html"
        out.write_text(html, encoding="utf-8")
        print(f"Built output/index.html")

    # Copy static assets
    src_css = root / "public" / "css"
    if src_css.exists():
        shutil.copytree(src_css, output_dir / "css", dirs_exist_ok=True)
