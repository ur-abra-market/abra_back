from ...schema import ApplicationSchema


class TokenConfirmation(ApplicationSchema):
    token: str
