import abc


class EventManager:
    def __init__(self):
        self.events = {}

    def register(self, event, handler):
        """Register an event and its handler in the events poll.

        When the event has already been defined, simply attach handler to the end of the list.

        :param event: the event to be triggered.
        :param handler: function, method or lambda that handles the event.
        :raise ValueError: if event or handler cannot be registered.
        """
        if not event or not handler:
            raise ValueError(
                    'Handler {%s} cannot be registered in event %s.' % (
                        handler, event))

        if event not in self.events:
            self.events[event] = []

        self.events[event].append(handler)

        return self

    def trigger(self, event, *args, **kwargs):
        """Trigger handlers associated with a specific event.

        :param event: the event to be triggered.
        :param args: positional arguments passed to the events.
        :param kwargs: key arguments passed to the events.
        """
        handlers = self.events.get(event, ())

        for handler in handlers:
            handler(*args, **kwargs)

        return self


class EventListener(metaclass=abc.ABCMeta):
    pass


class AppLifeCycleEventListener(EventListener, metaclass=abc.ABCMeta):
    @classmethod
    def on_app_start(cls):
        raise NotImplementedError

    @classmethod
    def on_app_end(cls):
        raise NotImplementedError

    @classmethod
    def on_app_dispose(cls):
        raise NotImplementedError


class RequestLifeCycleEventListener(EventListener, metaclass=abc.ABCMeta):
    @classmethod
    def on_request_start(cls):
        raise NotImplementedError

    @classmethod
    def on_request_end(cls):
        raise NotImplementedError

    @classmethod
    def on_request_dispose(cls):
        raise NotImplementedError
