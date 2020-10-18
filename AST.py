class AST(object):

    def __init__(self):
        self.depth = 0
        self.children = ()
        self.parents = ()

class Num(AST):

    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value

class Var(AST):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value


class UnOp(AST):

    def __init__(self, op, right):
        super().__init__()
        self.token = self.op = op
        self.depth = right.depth + 1
        self.children = (right)
        right.parents += (self,)

class BinOp(AST):

    def __init__(self, left, op, right):
        super().__init__()
        self.token = op
        self.depth = max(left.depth, right.depth) + 1
        self.children = (left, right)
        left.parents += (self,)
        right.parents += (self,)
