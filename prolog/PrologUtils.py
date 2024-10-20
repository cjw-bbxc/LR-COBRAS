import os
from threading import Lock

from pyswip import Prolog


class PrologUtils:

    def __init__(self):

        # 获取当前文件的路径
        current_path = os.path.dirname(__file__)

        self.path = str(current_path + '\ic.pl').replace('\\', '\\\\')

        self.prolog = Prolog()
        self.prolog.consult(self.path)
        self.lock = Lock()

    def add_must_link(self, x, y):
        with self.lock:
            x, y = self.change_type(x, y)
            querys = f"must_link({x}, {y}); must_link({y}, {x})"
            existing_facts = list(self.prolog.query(querys))
            if not existing_facts:
                relation = f"must_link({x}, {y})"
                self.prolog.assertz(relation)
                print(f'add must_link({x}-{y}) success')
            else:
                print('已存在')

    def add_cannot_link(self, x, y):
        with self.lock:
            x, y = self.change_type(x, y)
            querys = f"cannot_link({x}, {y}); cannot_link({y}, {x})"
            existing_facts = list(self.prolog.query(querys))
            if not existing_facts:
                relation = f"cannot_link({x}, {y})"
                self.prolog.assertz(relation)
                print(f'add cannot_link({x}-{y}) success')
            else:
                print('已存在')

    def valid_must_link(self, x):

        x = self.change_type(x)
        relation = "valid_must_link(" + x + ", X)"
        result = list(self.prolog.query(relation))
        print(result)
        return result

    def valid_all_must_link(self):

        result = list(self.prolog.query("valid_must_link(X, Y)"))
        # print(result)
        return result

    def conflict_link(self, x, y):

        x, y = self.change_type(x, y)
        relation = "conflict(X, Y)"
        list(self.prolog.query(relation))
        pass

    def conflict_all_link(self):

        result = list(self.prolog.query("conflict(X, Y)"))
        print(result)
        return result

    def change_type(self, x, y=None):
        x = str(x)
        if y is not None:
            y = str(y)
            return x, y
        else:
            return x
