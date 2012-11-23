# -*- coding: utf-8 -*-
class FlexQueue(list):

    def empty(self):
        if len(self) == 0:
            return True
        return False

    def qsize(self):
        return len(self)

    def get(self):
        if not self.empty():
            ret = self[0]
            self.remove(ret)
            return ret
        return None

    def put(self, item):
        self.append(item)

    def remove(self, item):
        if item in self:
            list.remove(self, item)
