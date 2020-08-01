def has_actions(action_object):
    """Raises an error if the action object does not have _actions"""
    if not hasattr(action_object, "_actions"):
        raise AttributeError(f"The object {action_object} does not have variable _actions")