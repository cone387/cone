import time


def timing(method):
    """
    :param method:
    :return:
    计算某函数耗时
    """
    def method_wrapper(*args, **kwargs):
        start_time = time.time()
        result = method(*args, **kwargs)
        print("[%s]%.02fs used" % (method.__name__, time.time() - start_time))
        return result
    return method_wrapper
