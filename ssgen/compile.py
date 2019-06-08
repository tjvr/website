
from .file import *
from .markdown import *
from .template import * 



def compile(pages: [BaseFile], directory="_site"):
    width = 60
    try:
        for f in pages:
            print("\rCompiling {}".format(f.path).ljust(width), end="")
            f = compile_page(f)
            f.write(directory)
        print("\rCompiled {} files".format(len(pages)).ljust(width), end="")
    finally:
        print()
    print("Wrote {}".format(directory))


def compile_page(page: BaseFile) -> BaseFile:
    if is_markdown(page):
        page = render_markdown(page)
    if is_templated(page):
        page = render_template(page)
    if is_html(page):
        page = rename_index_html(page)
    return page

