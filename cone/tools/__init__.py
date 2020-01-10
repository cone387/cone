import hashlib

def get_md5(string):
    if isinstance(string,str):
        string = string.encode("utf-8")
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()