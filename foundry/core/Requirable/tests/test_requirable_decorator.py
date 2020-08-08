

from foundry.core.Requirable.RequirableDecorator import RequirableDecorator


def test_initialization():
    """Tests if the requirement can initialize"""
    subject = RequirableDecorator(lambda *_: True)
    assert isinstance(subject, RequirableDecorator)


def test_attach_requirement():
    """Tests if we can attach an requirement"""
    subject = RequirableDecorator(lambda *_: True)
    subject.attach_requirement(lambda *_: True, 0)
    assert 0 in subject.requirements


def test_attach_random_requirement():
    """Tests if we can attach an requirement without specifying a key"""
    subject = RequirableDecorator(lambda *_: True)
    subject.attach_requirement(lambda *_: True)
    assert len(subject.requirements) == 1


def test_attach_multiple_requirements():
    """Tests if we can attach multiple requirements"""
    subject = RequirableDecorator(lambda *_: True)
    for _ in range(10):
        subject.attach_requirement(lambda *_: True)
    assert len(subject.requirements) == 10


def test_function_decoration():
    """Tests if the decorator can decorate a function"""
    subject = RequirableDecorator(lambda value: value + 1)
    assert subject(1) == 2


def test_attach_object_that_was_deleted():
    """Tests what happens if a class requirement is deleted"""
    class TestClass:
        """A basic class"""
        def test_func(self, value):
            """A function that does something"""
            return value

    subject = RequirableDecorator(lambda *_: True)
    test = TestClass()
    subject.attach_requirement(lambda *_: test.test_func(0))
    del test
    subject(0)


def test_no_same_id():
    """Tests if requirement can only have one id"""
    subject = RequirableDecorator(lambda *_: True)
    subject.attach_requirement(lambda *_: True, 0)
    subject.attach_requirement(lambda *_: True, 0)
    assert len(subject.requirements) == 1


def test_requirement_successful():
    """Tests if requirements are all True"""
    subject = RequirableDecorator(lambda *_: True)
    subject.attach_requirement(lambda *_: True, 0)
    assert subject()


def test_requirement_failed():
    """Tests if a single requirement has failed"""
    subject = RequirableDecorator(lambda *_: True)
    subject.attach_requirement(lambda *_: True, 0)
    assert subject()
    subject.attach_requirement(lambda *_: False)
    assert not subject()


def test_verify_function_call():
    """Tests if the requirement calls the function"""
    subject = RequirableDecorator(lambda *_: 27)
    subject.delete_requirement(True)
    assert subject() == 27


def test_requirement_deletion():
    """Tests if we can delete a requirement"""
    subject = RequirableDecorator(lambda *_: True)
    subject.attach_requirement(lambda *_: True, 0)
    subject.delete_requirement(0)
    assert len(subject.requirements) == 0
