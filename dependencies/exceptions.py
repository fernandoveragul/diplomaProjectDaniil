class InvalidFolderType(Exception):
    """Invalid type folder, valid types: [examples, tests, tutorials]"""
    def __repr__(self):
        return "Raised when the entered folder type is invalid"
