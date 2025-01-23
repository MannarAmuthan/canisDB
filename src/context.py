class Context:
    """A static class to hold and manage application-wide configuration."""
    _id = None
    _folder = ""
    _role = ""

    # Getters and Setters
    @classmethod
    def get_id(cls):
        return cls._id

    @classmethod
    def set_id(cls, value):
        cls._id = value

    @classmethod
    def get_folder(cls):
        return cls._folder

    @classmethod
    def set_folder(cls, value):
        cls._folder = value

    @classmethod
    def get_role(cls):
        return cls._role

    @classmethod
    def set_role(cls, value):
        cls._role = value
