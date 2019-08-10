
import os
import glob
from pprint import pprint
import sys
import time

import jinja2
from markupsafe import Markup

import ssgen


def make_pages():
    pages = []

    static_pages = ssgen.find_pages("pages/*")
    pages += static_pages

    menu = ssgen.make_menu(pages)

    # Copy redirects file into output folder
    pages += [ ssgen.get_file("_redirects") ]

    pages += [
        ssgen.get_file("assets/favicon.ico").rename("/favicon.ico"),
    ]

    pages += [
        ssgen.get_file("assets/bolt-white.svg"),
        ssgen.get_file("assets/livewires-black.svg"),
    ]
    pages += ssgen.find_files("assets/icon/*.png")
    pages += ssgen.find_files("assets/icon/*.svg")
    pages += ssgen.find_files("assets/font/*")

    pages += ssgen.find_files("assets/photo/*.jpg")

    stylesheet = open("templates/theme.css").read()
    stylesheet = stylesheet.replace("\n", " ")
    while "  " in stylesheet:
        stylesheet = stylesheet.replace("  ", " ")

    # Add site config & stylesheet to every page
    site = {
        # TODO override title for homepage
        "title": "LiveWires: technical activity holiday for 12–15s",
        "generated": int(time.time()),
        "color": "#2ba8d8",
        "menu": menu,
    }
    for page in pages:
        page.params['site'] = site
        page.params['stylesheet'] = stylesheet
        page.params['title'] = page.params.get('title') or site["title"]

    return pages


# Debug
for f in make_pages():
    print(f.path)
    params = f.params.copy()
    params.pop("stylesheet")
    pprint(params, depth=2)
    print()

# Build
ssgen.compile(make_pages(), "_site")

# Serve
if len(sys.argv) > 1 and sys.argv[1] == "-w":
    ssgen.serve(make_pages)

