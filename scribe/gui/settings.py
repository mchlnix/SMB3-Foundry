from PySide6.QtCore import QSettings


_settings = {
    "world view/show grid": False,
    "world view/show level pointers": False,
    "world view/show level previews": False,
    "world view/show sprites": True,
    "world view/show start position": False,
    "world view/show airship paths": 0,
    "world view/show pipes": False,
    "world view/show locks": False,
}


class Settings(QSettings):
    def __init__(self, organization="mchlnix", application="default"):
        super(Settings, self).__init__(organization, application)

        for key, default_value in _settings.items():
            if self.value(key) is None or self.is_default:
                self.setValue(key, default_value)

        self.sync()

    @property
    def is_default(self):
        return self.organizationName() == "mchlnix" and self.applicationName() == "default"

    def value(self, key: str, default_value=None, type_=None):
        if key in _settings and type_ is None:
            type_ = type(_settings[key])

        returned_value = super(Settings, self).value(key, default_value)

        if returned_value is None:
            return returned_value
        elif type_ is bool and isinstance(returned_value, str):
            # boolean values loaded from disk are returned as strings for some reason
            return returned_value == "true"
        else:
            return type_(returned_value)

    def setValue(self, key: str, value):
        return super(Settings, self).setValue(key, value)

    def sync(self):
        if self.is_default:
            return
        else:
            return super(Settings, self).sync()
