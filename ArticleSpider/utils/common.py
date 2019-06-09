# -*- coding: utf-8 -*-
_author_ = 'zhengqiang'

import hashlib


def get_md5(url):
    m = hashlib.md5()
    if isinstance(url, str):
        url = url.encode('utf-8')
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':
    url = "http://jobbole.com"
    print(get_md5(url))
