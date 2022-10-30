"""Helpers for working with HTTP."""
import io
import json
import os
import binascii
from urllib.parse import urlencode
from src.masonite.filesystem import UploadedFile


HTTP_STATUS_CODES = {
    100: "100 Continue",
    101: "101 Switching Protocol",
    102: "102 Processing",
    103: "Early Hints",
    200: "200 OK",
    201: "201 Created",
    202: "202 Accepted",
    203: "203 Non-Authoritative Information",
    204: "204 No Content",
    205: "205 Reset Content",
    206: "206 Partial Content",
    207: "207 Multi-Status",
    208: "208 Multi-Status",
    226: "226 IM Used",
    300: "300 Multiple Choice",
    301: "301 Moved Permanently",
    302: "302 Found",
    303: "303 See Other",
    304: "304 Not Modified",
    307: "307 Temporary Redirect",
    308: "308 Permanent Redirect",
    400: "400 Bad Request",
    401: "401 Unauthorized",
    402: "402 Payment Required",
    403: "403 Forbidden",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    406: "406 Not Acceptable",
    407: "407 Proxy Authentication Required",
    408: "408 Request Timeout",
    409: "409 Conflict",
    410: "410 Gone",
    411: "411 Length Required",
    412: "412 Precondition Failed",
    413: "413 Payload Too Large",
    414: "414 URI Too Long",
    415: "415 Unsupported Media Type",
    416: "416 Requested Range Not Satisfiable",
    417: "417 Expectation Failed",
    418: "418 I'm a teapot",
    421: "421 Misdirected Request",
    422: "422 Unprocessable Entity",
    423: "423 Locked",
    424: "424 Failed Dependency",
    425: "425 Too Early",
    426: "426 Upgrade Required",
    428: "428 Precondition Required",
    429: "429 Too Many Requests",
    431: "431 Request Header Fields Too Large",
    451: "451 Unavailable For Legal Reasons",
    500: "500 Internal Server Error",
    501: "501 Not Implemented",
    502: "502 Bad Gateway",
    503: "503 Service Unavailable",
    504: "504 Gateway Timeout",
    505: "505 HTTP Version Not Supported",
    506: "506 Variant Also Negotiates",
    507: "507 Insufficient Storage",
    508: "508 Loop Detected",
    510: "510 Not Extended",
    511: "511 Network Authentication Required",
}


def generate_wsgi(wsgi={}, path="/", query_string="", method="GET"):
    """Generate the WSGI environment dictionary that we receive from a HTTP request."""
    import io

    data = {
        "wsgi.version": (1, 0),
        "wsgi.multithread": False,
        "wsgi.multiprocess": True,
        "wsgi.run_once": False,
        "wsgi.input": io.BytesIO(),
        "SERVER_SOFTWARE": "gunicorn/19.7.1",
        "REQUEST_METHOD": method,
        "QUERY_STRING": query_string,
        "RAW_URI": path,
        "SERVER_PROTOCOL": "HTTP/1.1",
        "HTTP_HOST": "127.0.0.1:8000",
        "HTTP_ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "HTTP_UPGRADE_INSECURE_REQUESTS": "1",
        "HTTP_COOKIE": "",
        "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7",
        "HTTP_ACCEPT_LANGUAGE": "en-us",
        "HTTP_ACCEPT_ENCODING": "gzip, deflate",
        "HTTP_CONNECTION": "keep-alive",
        "wsgi.url_scheme": "http",
        "REMOTE_ADDR": "127.0.0.1",
        "REMOTE_PORT": "62241",
        "SERVER_NAME": "127.0.0.1",
        "SERVER_PORT": "8000",
        "PATH_INFO": path,
        "SCRIPT_NAME": "",
    }
    data.update(wsgi)
    return data


class RequestFile(UploadedFile):
    """High-level class to simulate a file coming from an HTTP request in tests."""

    def __init__(self, filename: str, mimetype: str, size=1024, content=None):
        if size:
            content = "a" * 1024
        super().__init__(filename, content, mimetype)


def encode_multipart_form_data(data):
    boundary = binascii.hexlify(os.urandom(16)).decode("ascii")
    encoded_data = ""
    for field, value in data.items():
        if isinstance(value, RequestFile):
            encoded_data += f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{value.filename}"\r\nContent-Type: {value.get_original_mimetype()}\r\n\r\n{value.get_content()}\r\n'
        else:
            encoded_data += f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"\r\n\r\n{value}\r\n'

    encoded_data += f"--{boundary}--\r\n\r\n"
    encoded_data = encoded_data.encode("utf-8")
    content_type = "multipart/form-data; boundary=%s" % boundary

    return encoded_data, content_type


def encode_www_form_urlencode_data(data):
    boundary = binascii.hexlify(os.urandom(16)).decode("ascii")
    url_data = urlencode(data)
    encoded_data = url_data.encode("utf-8")
    return encoded_data


def generate_wsgi_form_data(data={}, content_type="application/json"):
    if content_type == "application/json":
        wsgi_input = io.BytesIO(bytes(json.dumps(data), "utf-8"))
        content_length = len(str(json.dumps(data)))
    elif content_type == "multipart/form-data":
        encoded_data, content_type = encode_multipart_form_data(data)
        wsgi_input = io.BytesIO(encoded_data)
        content_length = str(len(encoded_data.decode("utf-8")))
    elif content_type == "application/x-www-form-urlencoded":
        encoded_data = encode_www_form_urlencode_data(data)
        wsgi_input = io.BytesIO(encoded_data)
        content_length = str(len(encoded_data.decode("utf-8")))
    else:
        wsgi_input = io.BytesIO(bytes(json.dumps(data), "utf-8"))
        content_length = len(str(json.dumps(data)))
    return {
        "wsgi.input": wsgi_input,
        "CONTENT_LENGTH": content_length,
        "CONTENT_TYPE": content_type,
    }
