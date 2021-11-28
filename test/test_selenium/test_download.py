import contextlib
import tempfile
import urllib
import urllib.request as request
from urllib.error import ContentTooShortError
from urllib.request import Request

_url_tempfiles = []


def urlretrieve(req, filename=None, reporthook=None, data=None):
    with contextlib.closing(request.urlopen(req, data)) as fp:
        headers = fp.info()

        # Just return the local path and the "headers" for file://
        # URLs. No sense in performing a copy unless requested.

        # Handle temporary file setup.
        if filename:
            tfp = open(filename, 'wb')
        else:
            tfp = tempfile.NamedTemporaryFile(delete=False)
            filename = tfp.name
            _url_tempfiles.append(filename)

        with tfp:
            result = filename, headers
            bs = 1024 * 8
            size = -1
            read = 0
            blocknum = 0
            if "content-length" in headers:
                size = int(headers["Content-Length"])

            if reporthook:
                reporthook(blocknum, bs, size)

            while True:
                block = fp.read(bs)
                if not block:
                    break
                read += len(block)
                tfp.write(block)
                blocknum += 1
                if reporthook:
                    reporthook(blocknum, bs, size)

    if size >= 0 and read < size:
        raise ContentTooShortError(
            "retrieval incomplete: got only %i out of %i bytes"
            % (read, size), result)

    return result


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
url = "https://images.pexels.com/videos/9917770/camp-sky-sunrise-sunset-9917770.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
req = Request(url=url, headers=headers)
urlretrieve(
    req,
    "./9917770.jpeg")
