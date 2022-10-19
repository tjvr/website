
from http.server import BaseHTTPRequestHandler
import shutil
from socketserver import TCPServer
from urllib.parse import urlparse, unquote

from .file import *
from .compile import *
from .template import is_html


class SiteHandler(BaseHTTPRequestHandler):
    def __init__(self, make_pages, *args):
        self.make_pages = make_pages
        super().__init__(*args)

    def find_page(self, request_path) -> BaseFile:
        pages = self.make_pages()
        for p in pages:
            file_path = "/".join(p.path.split(os.path.sep))
            if request_path == file_path:
                return p
            if request_path.rstrip("/") == file_path:
                return p

        return None

    def send_head(self):
        request_path = urlparse(self.path).path

        # Parse e.g. %20 so that we can serve files with spaces in the name
        request_path = unquote(request_path)

        page = self.find_page(request_path)
        if not page:
            self.send_error(404)
            return None

        if (is_html(page) or is_markdown(page)) and not request_path.endswith("/"):
            self.send_response(301)
            self.send_header("Location", page.path + "/")
            self.end_headers()
            return None

        page = compile_page(page)

        content_type = page.mime_type
        if content_type.startswith("text/"):
            content_type += "; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        return page

    def do_HEAD(self):
        self.send_head()

    def do_GET(self):
        page = self.send_head()
        if page:
            page.write_stream(self.wfile)



def serve(make_pages, port=8000, host="localhost"):
    def handler(*args):
        return SiteHandler(make_pages, *args)

    TCPServer.allow_reuse_address = True

    with TCPServer((host, port), handler) as srv:
        print("Listening on {}:{}".format(host, port))
        srv.serve_forever()

