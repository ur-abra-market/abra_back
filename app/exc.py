class ApplicationError(Exception):
    ...


class CRUDError(ApplicationError):
    ...


class ColumnNotFound(CRUDError):
    ...


class ResultRequired(CRUDError):
    ...
