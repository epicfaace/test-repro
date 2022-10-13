from collections import deque
import gzip
from io import BytesIO
from typing import Optional, IO

import indexed_gzip
import io

class BytesBuffer(BytesIO):
    """
    A class for a buffer of bytes. Unlike io.BytesIO(), this class
    keeps track of the buffer's size (in bytes).
    """

    def __init__(self):
        self.__buf = deque()
        self.__size = 0
        self.__pos = 0

    def __len__(self):
        return self.__size

    def write(self, data):
        self.__buf.append(data)
        self.__size += len(data)

    def read(self, size: Optional[int] = None):
        if size is None:
            size = self.__size
        ret_list = []
        while size > 0 and len(self.__buf):
            s = self.__buf.popleft()
            size -= len(s)
            ret_list.append(s)
        if size < 0:
            ret_list[-1], remainder = ret_list[-1][:size], ret_list[-1][size:]
            self.__buf.appendleft(remainder)
        ret = b''.join(ret_list)
        self.__size -= len(ret)
        self.__pos += len(ret)
        return ret

    def flush(self):
        pass

    def close(self):
        pass

    def tell(self):
        return self.__pos

    def __bool__(self):
        return True


class GzipStream(BytesIO):
    """A stream that gzips a file in chunks.
    """

    def __init__(self, fileobj: IO[bytes]):
        self.__input = fileobj
        self.__buffer = BytesBuffer()
        self.__gzip = gzip.GzipFile(None, mode='wb', fileobj=self.__buffer)

    def read(self, num_bytes=None) -> bytes:
        while num_bytes is None or len(self.__buffer) < num_bytes:
            s = self.__input.read(num_bytes)
            if not s:
                self.__gzip.close()
                break
            self.__gzip.write(s)
        return self.__buffer.read(num_bytes)

    def close(self):
        self.__input.close()

file_path = 'temp_file'

def test_indexed_gzip(file_path):
    source_fileobj = open(file_path, 'rb')
    def fn(*args, **kwargs):
        raise io.UnsupportedOperation
#     source_fileobj.seek = fn
#     source_fileobj.tell = fn
#     f = io.BytesIO(source_fileobj.read())
#     source_fileobj.seekable = lambda: False
#     source_fileobj.fileno = fn
    tar_file = indexed_gzip.IndexedGzipFile(fileobj=GzipStream(source_fileobj))
    tar_file.build_full_index()
#     while tar_file.read(1024 * 1024):
#         continue

test_indexed_gzip(file_path)
