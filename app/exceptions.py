class ApplicationError(Exception):
    """
    A base class for define errors
    """


class InvalidStatusId(ApplicationError):
    ...


class InvalidProductVariationId(ApplicationError):
    ...
