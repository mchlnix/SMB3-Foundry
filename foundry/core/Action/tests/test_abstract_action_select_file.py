

from .ActionSelectFileTest import ActionSelectFileTest
from .test_abstract_action_safe import warning_fail


class PathHolder:
    """A warning that changes"""
    def __init__(self, path: str) -> None:
        self.path = path

    def __call__(self, path: str) -> str:
        self.path = path
        return self.path


def test_initialization():
    """Tests if the object initializes"""
    ActionSelectFileTest("test", "path")


def test_attach_observer():
    """Tests if we can add an observer"""
    action = ActionSelectFileTest("test", "path")
    action.attach_observer(lambda path: path)
    assert len(action.file_selected_observer.observers) == 1


def test_delete_observer():
    """Tests if we can remove an observer"""
    action = ActionSelectFileTest("test", "path")
    action.file_selected_observer.attach_observer(lambda path: path, 1)
    action.file_selected_observer.delete_observable(1)
    assert len(action.file_selected_observer.observers) == 0


def test_action_call():
    """Tests if calling action works"""
    action = ActionSelectFileTest("test", "path")
    action.observable.observable()


def test_observer_receives_message():
    """Tests if the observers receive the message"""
    action = ActionSelectFileTest("test", "path")
    path_holder = PathHolder("")
    action.attach_observer(lambda path: path_holder(path))
    action.observable.observable()
    assert path_holder.path == "path"


def test_action_warning_attach():
    """Tests if we can add a warning"""
    action = ActionSelectFileTest("test", "path")
    action.attach_warning(lambda *_: warning_fail())


def test_action_warning_fail():
    """Tests if a warning fails properly"""
    action = ActionSelectFileTest("test", "path")
    action.attach_warning(lambda *_: warning_fail())
    action.warning_action.proceed = False
    path_holder = PathHolder("")
    action.attach_observer(lambda path: path_holder(path))
    action.observable.observable()
    assert path_holder.path == ""


def test_action_requirement_attach():
    """Tests if we can add a requirement"""
    action = ActionSelectFileTest("test", "path")
    action.attach_requirement(lambda *_: False)


def test_action_requirement_fail():
    """Tests if a requirement fails properly"""
    action = ActionSelectFileTest("test", "path")
    action.attach_requirement(lambda *_: False)
    path_holder = PathHolder("")
    action.attach_observer(lambda path: path_holder(path))
    action.observable.observable()
    assert path_holder.path == ""
