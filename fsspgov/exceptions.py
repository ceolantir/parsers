class RestartException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'RestartException, {self.message}'
        else:
            return 'RestartException has been raised.\n'


class IncorrectInputDataException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'IncorrectInputDataException, {self.message}'
        else:
            return 'IncorrectInputDataException has been raised.\n'
