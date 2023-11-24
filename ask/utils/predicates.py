from typing import Callable
from urllib.parse import urlparse


def join(*args):
    predicates = [a for a in args if a is Callable]
    return lambda x: all(p(x) for p in predicates)


def is_valid_url(url):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme) and bool(parsed_url.netloc)
