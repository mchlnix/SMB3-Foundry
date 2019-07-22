import abc
from abc import abstractmethod


class Undoable(abc.ABC):
    DONE = 0
    UNDONE = 1

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class LevelAction(Undoable):
    def __init__(self, obj, level):
        self.obj = obj
        self.level = level

        self.state = Undoable.UNDONE

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class AddObjectAction(LevelAction):
    def __init__(self, obj, level):
        super(AddObjectAction, self).__init__(obj, level)

    def do(self):
        pass

    def undo(self):
        pass


class RemoveObjectAction(LevelAction):
    def __init__(self, obj, level):
        super(RemoveObjectAction, self).__init__(obj, level)

    def do(self):
        pass

    def undo(self):
        pass


class MoveObjectAction(LevelAction):
    def __init__(self, obj, level):
        super(MoveObjectAction, self).__init__(obj, level)

    def do(self):
        pass

    def undo(self):
        pass


class ResizeObjectAction(LevelAction):
    def __init__(self, obj, level):
        super(ResizeObjectAction, self).__init__(obj, level)

    def do(self):
        pass

    def undo(self):
        pass


class ChangeObjectAction(LevelAction):
    def __init__(self, obj, level):
        super(ChangeObjectAction, self).__init__(obj, level)

    def do(self):
        pass

    def undo(self):
        pass
