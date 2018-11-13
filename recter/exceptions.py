

class WaitingTimeoutError(TimeoutError):
    """ Waiting timeout expired. """
    def __init__(self, *args, **kwargs):
        pass


class RunningTimeoutError(TimeoutError):
    """ Running timeout expired. """
    def __init__(self, previous: TimeoutError, *args, **kwargs):
        self.previous = previous
