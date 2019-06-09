
import os

from markupsafe import Markup
from misaka import Markdown, HtmlRenderer, smartypants, escape_html
from PIL import Image
import regex

from .file import BaseFile, MemoryFile


punctuation_re = regex.compile(r"[^\p{Word}\- ]", flags=regex.UNICODE)

def header_id(value):
    """
    1. Downcase the string
    2. Remove anything that is not a letter, number, space or hyphen (see the source for how Unicode is handled)
    3. Change any space to a hyphen
    """
    # TODO add -1, -2 etc to make it unique
    value = value.lower()
    value, _ = punctuation_re.subn("", value)
    return value.replace(" ", "-")

class CustomRenderer(HtmlRenderer):
    def image(self, link, title="", alt=""):
        maybe_alt = ' alt="%s"' % escape_html(alt) if alt else ''
        maybe_title = ' title="%s"' % escape_html(title) if title else ''
        url = escape_html(link)

        maybe_width = ""
        if url.startswith(os.path.sep):
            image = Image.open(url.lstrip(os.path.sep))
            width, height = image.size
            maybe_width = 'width="{}" height="{}" '.format(width, height)

        return '<img {}src="{}"{}{} />'.format(maybe_width, url, maybe_alt, maybe_title)

    def header(self, content, level):
        # content is already escaped
        id_ = header_id(Markup.unescape(content))
        return '<h{} id="{}">{}</h{}>'.format(
            level,
            escape_html(id_),
            content,
            level,
        )



renderer = CustomRenderer()
md = Markdown(renderer, extensions=('fenced-code',))


def is_markdown(f: BaseFile) -> bool:
    return f.mime_type == 'text/markdown'


def render_markdown(f: BaseFile) -> BaseFile:
    params = f.params.copy()

    # Render HTML
    markup = Markup(smartypants(md(f.content)))
    assert markup is not None

    # Strip extension
    new_path, ext = os.path.splitext(f.path)
    return MemoryFile(new_path, markup, params=params, mime_type='text/html')

