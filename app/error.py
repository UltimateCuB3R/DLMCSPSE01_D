"""Module for definition of exceptions unique to this application
"""


class TableNotKnownError(Exception):
    """Raise this exception if an unknown table name was given.
    """

    def __init__(self, message=None):
        """Calling the base class constructor.

        :param message: message to specify the error
        """

        super().__init__(message)


class ColumnNotKnownError(Exception):
    """Raise this exception if an unknown column name was given.
    """

    def __init__(self, message=None):
        """Calling the base class constructor.

        :param message: message to specify the error
        """

        super().__init__(message)


class DataMismatchError(Exception):
    """Raise this exception if mismatched data was given.
    """

    def __init__(self, message=None):
        """Calling the base class constructor.

        :param message: message to specify the error
        """

        super().__init__(message)


class NoDataFoundError(Exception):
    """Raise this exception if no data was found via SQL.
    """

    def __init__(self, message=None):
        """Calling the base class constructor.

        :param message: message to specify the error
        """

        super().__init__(message)


class ForbiddenActionError(Exception):
    """Raise this exception if a forbidden action was performed on an object.
    """

    def __init__(self, message=None):
        """Calling the base class constructor.

        :param message: message to specify the error
        """

        super().__init__(message)
