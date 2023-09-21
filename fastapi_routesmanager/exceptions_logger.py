from fastapi_routesmanager.routes_manager import RouteManager
import logging
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, List, Type, Optional

logger = logging.getLogger(__name__)


class ExceptionLogger(RouteManager):
    async def run(
            self,
            request: Request,
            call_next: Callable,
            remaining_managers: List[Type[RouteManager]],
    ) -> Optional[Response]:
        try:
            response: Response = await call_next(request, remaining_managers)
        except Exception as e:
            logger.exception(e)
            raise
        return response
