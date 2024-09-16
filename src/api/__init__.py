from .bids.views import bids_router
from .employees.views import employee_router
from .organization_responsibles.views import organization_responsibles_router
from .organizations.views import organization_router
from .pongs.views import pong_router
from .tenders.views import tenders_router

__all__ = (
    bids_router,
    employee_router,
    organization_router,
    pong_router,
    tenders_router,
    organization_responsibles_router,
    bids_router,
)
