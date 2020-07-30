"""
This module provides a way to easily create exclusivity for multiple observables
ExclusiveGroup: A class for merging multiple observables into one signal
"""

from typing import Optional, List, Hashable, Dict

from foundry.core.Observable import Observable

from foundry.gui.QCore.Action import AbstractActionObject, Action


class ExclusiveGroup(AbstractActionObject):
    """A group of observables that have identifiers opposed that produce a single output"""
    update_action: Action
    subscriptions: Dict
    _last_selected: Optional[Hashable]
    _index: int

    def __init__(self, observables: Optional[List[Observable]] = None) -> None:
        super(AbstractActionObject, self).__init__()
        if observables is None:
            observables = []
        self._last_selected = None
        self._index = 0
        self.subscriptions = {}
        self.add_observables(observables)

    def add_observables(self, observables: List[Observable]) -> None:
        """Adds a group of observables"""
        for observable in observables:
            self.add_observable(observable)

    def add_observable(self, observable: Observable) -> None:
        """Adds a single observable"""
        self.add_observable_with_return(observable, self._index)
        self._index += 1

    def add_observable_with_return(self, observable: Observable, identifier: Hashable) -> None:
        """Provides the interface for special returns, but must be hashable"""
        observable.attach(lambda *_: setattr(self, "_last_selected", identifier))
        observable.attach(lambda *_: self.update_action.observer(identifier))
        self.subscriptions.update({identifier: observable})

    @property
    def last_selected(self) -> Optional[Hashable]:
        """Returns the last item selected"""
        return self._last_selected

    @last_selected.setter
    def last_selected(self, selected: Hashable) -> None:
        self._last_selected = selected
        self.update_action.observer(selected)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("update", Observable(lambda *_: self.last_selected)),
        ]










