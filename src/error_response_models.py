import json

from fastapi import Response, status

import consts


class BaseErrorResponse(Response):
    def __init__(self, status_code: int, content: str):
        self.content = content
        super().__init__(
            status_code=status_code,
            content=self.__dump_content_info(),
            media_type="application/json",
        )

    def __dump_content_info(self):
        try:
            data = json.dumps({"reason": self.content})
        except json.JSONEncoder:
            return "Неверные данные для дампа в json "
        return data


class BadRequestErrorResponse(BaseErrorResponse):
    def __init__(self, content: str = consts.BAD_REQUEST_CONTENT):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, content=content)


class UserNotExistErrorResponse(BaseErrorResponse):
    def __init__(self, content: str = consts.USER_NOT_FOUND_CONTENT):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, content=content)


class OrganizationNotExistErrorResponse(BaseErrorResponse):
    def __init__(self, content: str = consts.ORGANIZATION_NOT_FOUND_CONTENT):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, content=content)


class TenderNotExistErrorResponse(BaseErrorResponse):
    def __init__(self, content: str = consts.TENDER_NOT_FOUND_CONTENT):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, content=content)


class BidNotExistErrorResponse(BaseErrorResponse):
    def __init__(self, content: str = consts.BID_NOT_FOUND_CONTENT):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, content=content)


class UserIsNotResponsibleForOrganizationErrorResponse(BaseErrorResponse):
    def __init__(
        self, content: str = consts.USER_IS_NOT_RESPONSIBLE_ORGANIZATION_CONTENT
    ):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, content=content)


class UserIsNotResponsibleForTenderErrorResponse(BaseErrorResponse):
    def __init__(self, content: str = consts.USER_IS_NOT_RESPONSIBLE_TENDER_CONTENT):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, content=content)


class UserIsNotResponsibleForBidErrorResponse(BaseErrorResponse):
    def __init__(self, content: str = consts.USER_IS_NOT_RESPONSIBLE_BID_CONTENT):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, content=content)


class ForbiddenErrorResponse(BaseErrorResponse):
    def __init__(self, content: str = consts.FORBIDDEN_ACCESS_CONTENT):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, content=content)
