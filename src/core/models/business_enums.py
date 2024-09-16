from enum import Enum


class OrganizationType(Enum):
    IE = "IE"
    LLC = "LLC"
    JSC = "JSC"


class ServiceType(Enum):
    CONSTRUCTION = "Construction"
    DELIVERY = "Delivery"
    MANUFACTURE = "Manufacture"


class TenderStatus(Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CLOSED = "Closed"


class BidStatus(Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CANCELED = "Canceled"


class AuthorType(Enum):
    ORGANIZATION = "Organization"
    USER = "User"


class DecisionType(Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
