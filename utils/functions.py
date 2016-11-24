class DelayedFunction:
    def __init__(self, fct, *args):
        self.func = fct
        self.args = args

    def exec(self):
        return self.func(*self.args)
