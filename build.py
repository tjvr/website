
import os
import glob
from pprint import pprint
import sys
import time

import jinja2
from markupsafe import Markup

import ssgen


def make_pages(embed_css=False):
    pages = []

    static_pages = ssgen.find_pages("pages/*")
    pages += static_pages

    menu = ssgen.make_menu(pages)

    # Copy redirects file into output folder
    pages += [ ssgen.get_file("_redirects") ]

    pages += [
        ssgen.get_file("assets/favicon.ico").rename("/favicon.ico"),
        ssgen.get_file("assets/bolt-white.svg"),
        ssgen.get_file("assets/livewires-black.svg"),
        ssgen.get_file("assets/livewires-og.jpg"),
    ]
    pages += ssgen.find_files("assets/icon/*.*")
    pages += ssgen.find_files("assets/font/*.*")
    pages += ssgen.find_files("assets/photo/*.*")
    pages += ssgen.find_files("assets/photo/2022/*.*")
    pages += ssgen.find_files("assets/pdf/*.*")

    if embed_css:
        stylesheet = open("templates/theme.css").read()
        stylesheet = stylesheet.replace("\n", " ")
        while "  " in stylesheet:
            stylesheet = stylesheet.replace("  ", " ")
    else:
        pages += [
            ssgen.get_file("templates/theme.css").rename("/theme.css")
        ]

    # Add site config & stylesheet to every page
    site = {
        "title": "LiveWires",
        "twitter": "@livewireshol",
        "generated": int(time.time()),
        "color": "#2ba8d8",
        "url": os.environ.get("DEPLOY_PRIME_URL", "http://localhost:8000"),
    }
    for page in pages:
        page.params['site'] = site
        if embed_css:
            page.params['stylesheet'] = stylesheet
        page.params['title'] = page.params.get('title') or site["title"]

    return pages


# Debug
watch_mode = len(sys.argv) > 1 and sys.argv[1] == "-w"
for f in make_pages(embed_css=False):
    print(f.path)
    pprint(f.params, depth=2)
    print()

# Build
ssgen.compile(make_pages(embed_css=True), "_site")

# Serve
if watch_mode:
    ssgen.serve(make_pages, host="0.0.0.0")

