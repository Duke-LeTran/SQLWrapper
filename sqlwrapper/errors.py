class YesNoParseError(Exception):
    """
    Raise when parsing error.
    """
    def __init__(self):
        self.message=f"Error parsing 'yes' or 'no' answer."
        super().__init__(self.message)


class FailedInsertMissingTable(Exception):
    """Raised when attemps to insert pandas df but table is not defined"""
    pass

class Missing_DBCONFIG_ValueError(Exception):
    """raised when a value is missing"""
    pass