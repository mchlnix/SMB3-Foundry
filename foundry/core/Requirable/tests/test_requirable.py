

from foundry.core.Requirable.Requirable import Requirable


def test_initialization():
    """Tests if the requirement can initialize"""
    subject = Requirable()
    assert isinstance(subject, Requirable)


def test_attach_requirement():
    """Tests if we can attach an requirement"""
    subject = Requirable()
    subject.attach_required(lambda *_: True, 0)
    assert 0 in subject.requirements


def test_attach_random_requirement():
    """Tests if we can attach an requirement without specifying a key"""
    subject = Requirable()
    subject.attach_required(lambda *_: True)
    assert len(subject.requirements) == 1


def test_attach_multiple_requirements():
    """Tests if we can attach multiple requirements"""
    subject = Requirable()
    for _ in range(10):
        subject.attach_required(lambda *_: True)
    assert len(subject.requirements) == 10


def test_attach_object_that_was_deleted():
    """Tests what happens if a class requirement is deleted"""
    class TestClass:
        """A basic class"""
        def test_func(self, value):
            """A function that does something"""
            return value

    subject = Requirable()
    test = TestClass()
    subject.attach_required(lambda *_: test.test_func(0))
    del test
    subject(0)


def test_no_same_id():
    """Tests if requirement can only have one id"""
    subject = Requirable()
    subject.attach_required(lambda *_: True, 0)
    subject.attach_required(lambda *_: True, 0)
    assert len(subject.requirements) == 1


def test_requirement_successful():
    """Tests if requirements are all True"""
    subject = Requirable()
    subject.attach_required(lambda *_: True, 0)
    assert subject()


def test_requirement_failed():
    """Tests if a single requirement has failed"""
    subject = Requirable()
    subject.attach_required(lambda *_: True, 0)
    assert subject()
    subject.attach_required(lambda *_: False)
    assert not subject()


def test_requirement_deletion():
    """Tests if we can delete a requirement"""
    subject = Requirable()
    subject.attach_required(lambda *_: True, 0)
    subject.delete_required(0)
    assert len(subject.requirements) == 0
