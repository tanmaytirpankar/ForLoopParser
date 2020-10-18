class SymbolTable(object):
    __slots__ = ['_symTab', '_scope', '_scopeCond']

    def __init__(self, scope=0, cond=0, caller_symTab=None):
        self._scope = scope
        self._symTab = {}
        self._scopeCond = cond
        self._symTab['_caller_'] = caller_symTab

    def insert(self, symbol, val):
        self._symTab[symbol] = val

    def lookup(self, symbol):
        if self._symTab['_caller_'] is None:
            return self._symTab.get(symbol)

        return self._symTab.get(symbol, self._symTab['_caller_'].lookup(symbol))
