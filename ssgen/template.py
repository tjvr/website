
import os

from markupsafe import Markup, escape
import jinja2
import smartypants

from .file import BaseFile, MemoryFile



env = jinja2.Environment(
    loader = jinja2.FileSystemLoader('./templates'),
    autoescape = jinja2.select_autoescape(['html', 'xml']),
)

def smartypants_filter(text):
    if not text:
        return ""
    return smartypants.smartypants(text, smartypants.Attr.default | smartypants.Attr.u)
env.filters['smartypants'] = smartypants_filter


def is_html(f: BaseFile) -> bool:
    return f.mime_type == 'text/html'


def is_templated(f: BaseFile) -> bool:
    return is_html(f) or f.params.get("template")


def rename_index_html(f: BaseFile, index='index.html') -> BaseFile:
    # Strip extension + add /index.html
    rest, ext = os.path.splitext(f.path)
    new_path = os.path.join(rest, index)
    return f.rename(new_path, f.params)


def render_template(f: BaseFile, default_template='default.html') -> BaseFile:
    params = f.params
    try:
        content = f.content
    except:
        import pdb; pdb.set_trace()

    # Find template
    template_name = params.get('template', default_template)
    template = env.get_template(template_name)

    # Render
    markup = template.render(content=content, **params)

    return MemoryFile(f.path, markup, params=params, mime_type=f.mime_type)

