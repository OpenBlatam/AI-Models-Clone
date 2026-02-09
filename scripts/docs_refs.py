from __future__ import annotations

import argparse
import webbrowser
from importlib import metadata


DOCS = {
    "torch": "https://pytorch.org/docs/stable/index.html",
    "transformers": "https://huggingface.co/docs/transformers/index",
    "diffusers": "https://huggingface.co/docs/diffusers/index",
    "gradio": "https://www.gradio.app/docs",
}


def print_refs() -> None:
    rows = []
    for pkg, url in DOCS.items():
        try:
            ver = metadata.version(pkg)
        except Exception:
            ver = "not-installed"
        rows.append(f"{pkg} ({ver}): {url}")
    print("\n".join(rows))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print official docs URLs; optionally open in browser")
    parser.add_argument("--open", choices=list(DOCS.keys()) + ["all"], help="Open specified docs in default browser")
    args = parser.parse_args()

    print_refs()
    if args.open:
        keys = list(DOCS.keys()) if args.open == "all" else [args.open]
        for k in keys:
            webbrowser.open(DOCS[k])


if __name__ == "__main__":
    main()



