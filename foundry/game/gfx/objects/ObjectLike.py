import abc


class ObjectLike(abc.ABC):
    obj_index: int
    domain: int

    is_4byte: bool

    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def draw(self, dc, zoom, transparent):
        pass

    @abc.abstractmethod
    def get_status_info(self):
        pass

    @abc.abstractmethod
    def set_position(self, x, y):
        pass

    @abc.abstractmethod
    def move_by(self, dx, dy):
        pass

    @abc.abstractmethod
    def get_position(self):
        pass

    @abc.abstractmethod
    def resize_to(self, x, y):
        pass

    @abc.abstractmethod
    def resize_by(self, dx, dy):
        pass

    @abc.abstractmethod
    def point_in(self, x, y):
        pass

    @abc.abstractmethod
    def get_rect(self):
        pass

    @abc.abstractmethod
    def change_type(self, new_type):
        pass

    @abc.abstractmethod
    def __contains__(self, point):
        pass

    @abc.abstractmethod
    def to_bytes(self):
        pass
