class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class SomethingNotSetError(Error):
    """Exception raised for errors in the input of transformations.

    Attributes:
        where -- where is something missing
        what     -- what is missing
    """

    def __init__(self, where, what):
        self.where = where
        self.what = what

    def __str__(self):
        return "{0} not set in {1}".format(self.what, self.where)


class ProjectionNotSetError(SomethingNotSetError):
    what = 'Projection'


class GeoTransformNotSetError(SomethingNotSetError):
    what = 'GeoTransform'
