

class WaitingTimeoutError(TimeoutError):
    """ Waiting timeout expired. """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass


class RunningTimeoutError(TimeoutError):
    """ Running timeout expired. """
    def __init__(self, previous: TimeoutError, *args, **kwargs): # real signature unknown
        self.previous = previous
