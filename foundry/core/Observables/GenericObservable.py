

from functools import partialmethod

from foundry.core.Observables.Observable import Observable
from foundry.core.Observables.core.attach_observer import attach_observer
from foundry.core.Observables.core.notify_observers import notify_observers
from foundry.core.Observables.core.delete_observer import delete_observer


class GenericObservable(Observable):
    """
    An observable with generic concrete methods already instantiated, only requiring a name
    """

    __init__ = partialmethod(Observable.__init__, notify_observers, attach_observer, delete_observer)
