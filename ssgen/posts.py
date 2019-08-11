
from datetime import datetime
import glob
import os
import regex

import yaml

from .file import BaseFile, LazyFile, MemoryFile
from .markdown import is_markdown
from .template import is_html



date_re = regex.compile(r'(?:([0-9]{4}-[0-9]{2}-[0-9]{2})-)?(.*)')
draft_re = regex.compile(r'(draft--?)?(.*)')

front_matter_re = regex.compile(r'^(?:[ \t\n]*---+[ \t]*\n(?:(.*?)\n)?[ \t]*---+[ \t]*\n)?(.*)', regex.DOTALL)
assert front_matter_re.fullmatch("\n---\nfoo\n---\nbar\n---\nquxx").groups() == ("foo", "bar\n---\nquxx")
assert front_matter_re.fullmatch("-----\n---\nbar").groups() == (None, "bar")
assert front_matter_re.fullmatch("quxx").groups() == (None, "quxx")


def empty_index_file(path, params=None) -> BaseFile:
    return empty_file(path, "text/html", params)

def empty_file(path, mime_type, params=None) -> BaseFile:
    params = dict(params) if params else {}
    return MemoryFile(path, "", params, mime_type)

def get_file(path) -> BaseFile:
    return LazyFile(path)

def find_files(pattern) -> [BaseFile]:
    return [LazyFile(path)
            for path in glob.glob(pattern)]


def make_menu(pages=[BaseFile]) -> [dict]:
    # Menu includes every page except the index page
    menu = [f.params for f in pages if f.params.get("menu_title")]

    # Sort menu by page order (if set)
    for params in menu:
        params["order"] = params.get("order", 0)
    menu.sort(key=lambda params: params["order"])

    return menu


def find_pages(pattern='./pages/*', default_template='page.html') -> [BaseFile]:
    try:
        pages = [render_page(f, default_template=default_template) for f in find_files(pattern)]
        print("\rRead {} pages".format(len(pages)).ljust(60), end="")
    finally:
        print()
    return pages


def find_tags(posts: [dict], pattern='./tags/*', base="/tag/", default_template='tag.html') -> [BaseFile]:
    used_tags = set()
    for post in posts:
        for tag in post.get("tags", []):
            used_tags.add(tag)

    try:
        tag_pages = [render_page(f, default_template=default_template, base=base) for f in find_files(pattern)]
        print("\rRead {} tags".format(len(posts)).ljust(60), end="")
    finally:
        print()

    # If a tag appears in a post but doesn't have a custom index page, make an
    # empty page for it
    found_tags = set(page.params['slug'] for page in tag_pages)
    missing_tags = used_tags - found_tags
    for tag in missing_tags:
        url = base + tag
        tag_pages.append(empty_index_file(url, {
            "title": tag,
            "slug": tag,
            "url": url,
            "template": default_template,
        }))

    # Add posts to each page
    for page in tag_pages:
        tag = page.params["slug"]
        page.params["posts"] = [p for p in posts if tag in p.get("tags", [])]

    return tag_pages


def find_posts(pattern='./posts/*', default_template='post.html') -> [BaseFile]:
    try:
        posts = [render_page(f, default_template=default_template) for f in find_files(pattern)]
        print("\rRead {} posts".format(len(posts)).ljust(60), end="")
    finally:
        print()

    # Sort newest first
    posts.sort(key=lambda f: f.params.get('date', '9999'), reverse=True)

    # Remove deleted posts
    posts = [f for f in posts if not f.params.get('deleted')]

    # Number posts
    for number, f in enumerate(posts, 1):
        f.params['number'] = number

    # Add map for finding related posts
    shallow_params = [f.params.copy() for f in posts]
    posts_by_slug = {}
    for params in shallow_params:
        posts_by_slug[params['slug']] = params
    for f in posts:
        f.params['posts_by_slug'] = posts_by_slug

    # Hide draft posts from the index
    published_posts = [f for f in posts if not f.params.get('draft')]
    shallow_params = [f.params.copy() for f in published_posts]

    # Add next/prev links
    for index, f in enumerate(published_posts):
        if index > 0:
            f.params['next'] = shallow_params[index - 1]
        if index + 1 < len(published_posts):
            f.params['prev'] = shallow_params[index + 1]

    return [f.params for f in published_posts], posts


def render_page(f: BaseFile, default_template='default.html', base="/") -> BaseFile:
    print("\rReading {}".format(f.path).ljust(60), end="")

    params = f.params
    rest, name = os.path.split(f.path)
    name, ext = os.path.splitext(name)

    # Extract the date and slug from the filename
    # Or alternatively the `draft--` component
    date, slug = date_re.fullmatch(name).groups()
    if date:
        params['date'] = date
    else:
        draft, slug = draft_re.fullmatch(name).groups()
        params['draft'] = draft

    if slug == 'index':
        slug = ''
    params['slug'] = slug

    # Set default title
    params['title'] = slug

    # Set default post template
    params['template'] = default_template

    # Only check for front matter in Markdown and HTML files
    if not is_markdown(f) and not is_html(f):
        return f.rename(slug, params)

    # Parse front matter
    content = f.content
    front_matter, source = front_matter_re.fullmatch(content).groups()
    if front_matter:
        file_params = yaml.load(front_matter)
        params.update(file_params)

    # Front matter can override the slug
    slug = params['slug']
    params['url'] = (base + slug + "/") if slug else "/"

    # Split up tags array
    if not isinstance(params.get("tags", None), list):
        tags_str = params.get("tags", "").strip()
        params['tags'] = tags_str.split(" ") if tags_str else []

    # Front matter can override the date
    try:
        date = params.get('date', "")
        if not date:
            date = datetime.now().date()
        elif isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        params['date'] = date
    except ValueError:
        pass

    return MemoryFile(os.path.join(base, slug), source, params=params, mime_type=f.mime_type)
 
