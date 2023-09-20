from .routes_manager import RouteManager
import logging
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, List, Type, Optional

logger = logging.getLogger(__name__)


class HeadersLogger(RouteManager):
    async def run(
            self,
            request: Request,
            call_next: Callable,
            remaining_managers: List[Type[RouteManager]],
    ) -> Optional[Response]:
        logger.debug("Requests headers: " + str(request.headers))
        response: Response = await call_next(request, remaining_managers)
        logger.debug("Response headers: " + str(response.headers))
        return response
