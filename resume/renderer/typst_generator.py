"""Generate Typst resume PDF from YAML data."""
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _section_title(lines, title: str) -> None:
    lines.append(f'#set text(fill: rgb("#4f46e5"))')
    lines.append(f"#text(size: 13pt, weight: 'bold')[{title}]")
    lines.append(f'#set text(fill: black)')
    lines.append('#v(0.3em)')
    lines.append('#line(length: 100%, stroke: 0.5pt + rgb("#d0d7de"))')
    lines.append('#v(0.3em)')


def generate(locale: str) -> None:
    with open(ROOT / "data" / locale / "main.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    lines: list[str] = []
    lines.append('#set page(paper: "a4", margin: (x: 2.5cm, y: 2.5cm))')
    lines.append('#set text(size: 10pt, font: ("Helvetica", "Arial"))')
    lines.append('#set par(justify: true)')
    lines.append('#set heading(numbering: none)')
    lines.append("")
    lines.append(f'#align(center)[#text(size: 22pt, weight: "bold")[{_escape(data["name"])}]]')
    lines.append("")
    for b in data["bio"].strip().splitlines():
        stripped = b.strip()
        if stripped.startswith("*"):
            stripped = stripped.lstrip("* ").strip()
        lines.append(f"- {_escape(stripped)}")
    lines.append("")
    lines.append('#v(0.5em)')

    lines.append(f'#text(weight: "bold")[Contact: {_escape(data["email"])} · {_escape(data["location"])}]')
    lines.append('#v(0.8em)')

    _section_title(lines, data["t"]["work_experience"])
    for job in data["work_experience"]:
        lines.append(f'#text(weight: "bold")[{_escape(job["position"])}, {_escape(job["company"])}]  #text(fill: rgb("#8b949e"))[{_escape(job["start"])} - {_escape(job["end"])}]')
        for item in job["content"].strip().splitlines():
            stripped = item.strip()
            if stripped.startswith("*"):
                stripped = stripped.lstrip("* ").strip()
            lines.append(f"- {_escape(stripped)}")
        lines.append("")

    _section_title(lines, data["t"]["education"])
    for e in data["education"]:
        lines.append(f'#text(weight: "bold")[{_escape(e["school"])}]  #text(fill: rgb("#8b949e"))[{_escape(e["start"])} - {_escape(e["end"])}]')
        lines.append(f'{_escape(e["major"])} / {_escape(e["degree"])}')
        for line in e["content"].strip().splitlines():
            lines.append(_escape(line.strip()))
        lines.append("")

    _section_title(lines, data["t"]["stack"])
    lines.append(", ".join(_escape(s) for s in data["stack"]))
    lines.append("")

    _section_title(lines, data["t"]["skills"])
    for skill in data["skills"]:
        lines.append(f'{_escape(skill["name"])}: {"█" * int(skill["value"] // 10)}{"░" * (10 - int(skill["value"] // 10))} {skill["value"]}%')

    typ = "\n".join(lines)
    typ_path = ROOT / f"resume_{locale}.typ"
    typ_path.write_text(typ, encoding="utf-8")
    subprocess.run(
        ["typst", "compile", str(typ_path), str(ROOT / f"resume_{locale}.pdf")],
        check=True,
    )
    print(f"Generated resume_{locale}.pdf")


if __name__ == "__main__":
    generate("en")