
import io
import os
import mimetypes

from markupsafe import Markup



class BaseFile:
    @property
    def path(self):
        if getattr(self, '_path', None):
            return self._path
        raise NotImplementedError(self.__class__.__name__)

    @property
    def relative_path(self):
        return self.path.lstrip(os.path.sep)

    @property
    def mime_type(self):
        if getattr(self, '_mime_type', None):
            return self._mime_type
        t, _ = mimetypes.guess_type(self.relative_path, strict=False)
        if t == 'application/xhtml+xml':
            return 'text/html'
        if t:
            return t
        return ""

    @property
    def content(self):
        if getattr(self, '_content', None) is not None:
            return self._content
        raise NotImplementedError(self.__class__.__name__)

    @property
    def stream(self):
        content = self.content
        if isinstance(content, (str, Markup)):
            content = content.encode('utf-8')
        return io.BytesIO(content)
        raise NotImplementedError(self.__class__.__name__)

    @property
    def params(self):
        return getattr(self, '_params', {})

    def rename(self, path, params):
        params = dict(params) if params else {}
        return MemoryFile(path, self.content, params, self.mime_type)

    def write(self, root='.'):
        output_path = os.path.join(root, self.relative_path)

        output_dir = os.path.dirname(output_path)
        if os.path.isfile(output_dir):
            os.remove(output_dir)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        if self.mime_type.startswith('text/'):
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            return

        with open(output_path, 'wb') as f:
            self.write_stream(f)

    def write_stream(self, output_file):
        s = self.stream
        while True:
            chunk = s.read(4096)
            if chunk == b'':
                return
            output_file.write(chunk)


class LazyFile(BaseFile):
    def __init__(self, path, params=None, is_binary=False):
        self._path = os.path.join('/', path)
        self._params = dict(params) if params else {}

    @property
    def stream(self):
        return open(self.relative_path, 'rb')

    @property
    def content(self):
        is_binary = not self.mime_type.startswith('text/')
        if is_binary:
            with open(self.relative_path, 'rb') as f:
                return f.read()

        with open(self.relative_path, 'r', encoding='utf-8') as f:
            return f.read()

    def rename(self, path, params=None):
        params = dict(params) if params else {}
        return ProxyFile(path, params, self)


class MemoryFile(BaseFile):
    def __init__(self, path, content, params=None, mime_type=None):
        if content is None:
            raise ValueError("File content cannot be None")
        self._path = os.path.join('/', path)
        self._content = content
        self._params = dict(params) if params else {}
        self._mime_type = mime_type


class ProxyFile(BaseFile):
    def __init__(self, path, params, file: BaseFile):
        self._path = os.path.join('/', path)
        self._params = dict(params) if params else {}
        self._file = file

    @property
    def mime_type(self):
        return self._file.mime_type

    @property
    def stream(self):
        return self._file.stream

    @property
    def content(self):
        return self._file.content

    def write(self, *args, **kwargs):
        return self._file.write(*args, **kwargs)



def is_binary_stream(s) -> bool:
    if isinstance(s, (io.RawIOBase, io.BufferedIOBase)):
        return True
    return 'b' in s.mode



