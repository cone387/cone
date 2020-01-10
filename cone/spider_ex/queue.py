
_DOWNLOAD_QUEUE = None
_RECORD_QUEUE = None

def get_dowonload_queue():
    return _DOWNLOAD_QUEUE


def set_download_queue(queue):
    global _DOWNLOAD_QUEUE
    _DOWNLOAD_QUEUE = queue


def get_record_queue():
    return _RECORD_QUEUE


def set_record_queue(queue):
    global _RECORD_QUEUE
    _RECORD_QUEUE = queue

