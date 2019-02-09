

class Priority:
    def __init__(self, priority=0):
        self.priority = priority

    def __lt__(self, other):
        return self.priority > other.priority

    def __str__(self):
        return str(self.priority)