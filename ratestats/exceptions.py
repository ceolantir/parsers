class DateDeltaError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'DateDeltaError, {self.message}'
        else:
            return 'DateDeltaError has been raised.\n'
