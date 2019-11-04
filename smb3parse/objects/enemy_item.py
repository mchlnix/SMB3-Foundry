from smb3parse.objects import InLevelObject


class EnemyItem(InLevelObject):
    def __init__(self, data):
        super(EnemyItem, self).__init__(data)

        if not len(data) == 3:
            raise ValueError(f"Length of the given data must be 3, was {len(data)}.")

        self.domain = 0

        self._id, self._x, self._y = data
