class NullPool(object):
    def __init__(self, *args, **kwargs):
        pass

    def map(self, fn, args):
        return map(fn, args)
