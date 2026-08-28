class DomainError(Exception):
    """Base exception for expected business-rule failures."""


class DuplicateAttendanceError(DomainError):
    pass


class AttendanceOrderError(DomainError):
    pass


class InvalidTaskFormatError(DomainError):
    pass


class FAQConfigurationError(DomainError):
    pass


class MattermostAPIError(DomainError):
    pass

