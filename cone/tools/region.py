import json
import time
import sys


# 强扭的瓜-不甜
class RegionHelper(object):
    def __init__(self):
        self.region = self.load_region(r'F:\Python36\Lib\cone\tools\region.txt')
    
    @classmethod
    def load_region(cls, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def search(self, target, is_equal=False):
        # print(region, region in self.region)
        if is_equal:
            search = self._search_equal
        else:
            search = self._search
        start_time = time.time()
        paths = []
        path = ["中国"]
        region = self.region.copy()
        while search(target, region, path):
            paths.append(path)
            del region[path[1]]
            path = ["中国"]
        print("search end. use %.2fs"%(time.time() - start_time))
        return paths

    def _search_equal(self, target, region, path):
        for key in region.keys():
            if target == key:
                path.append(key)
                return True
        parents = region.keys()
        children = region.values()
        for parent, region in zip(parents, children):
            path.append(parent)
            if self._search_equal(target, region, path):
                return True
            else:
                path.pop()
        return False

    def _search(self, target, region, path):
        for key in region.keys():
            if target in key:
                path.append(key)
                return True
        parents = region.keys()
        children = region.values()
        for parent, region in zip(parents, children):
            path.append(parent)
            if self._search(target, region, path):
                return True
            else:
                path.pop()
        return False


if __name__ == '__main__':
    region = sys.argv[1]
    try:
        is_equal = sys.argv[2] == 'equal'
    except:
        is_equal = False
    paths = RegionHelper().search(region, is_equal=is_equal)
    if not paths:
        print(f'not found {region}')
    for path in paths:
        print("->".join(path))