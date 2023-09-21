import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Type, Coroutine

from fastapi import APIRouter, Request, Response
from fastapi.routing import APIRoute


class RouteManager(ABC):
    # TODO: Documentame
    @abstractmethod
    async def run(self, request: Request, call_next: Callable, remaining_managers: List) -> Response:
        response: Response = await call_next(request, remaining_managers)
        return response


class RouteManagersRegistry:
    # TODO: Documentame
    __route_managers: list = []

    @staticmethod
    def register_route_manager(manager_class: Type[RouteManager]) -> None:
        if manager_class not in RouteManagersRegistry.__route_managers:
            RouteManagersRegistry.__route_managers.append(manager_class)

    @staticmethod
    def register_route_managers(managers_list: List[Type[RouteManager]]) -> None:
        for manager in managers_list:
            RouteManagersRegistry.register_route_manager(manager)

    @staticmethod
    def remove_route_manager(manager_class: Type[RouteManager]) -> None:
        if manager_class in RouteManagersRegistry.__route_managers:
            del RouteManagersRegistry.__route_managers[RouteManagersRegistry.__route_managers.index(manager_class)]

    @staticmethod
    def get_managers() -> list:
        return RouteManagersRegistry.__route_managers.copy()


class ManagedRoute(APIRoute):
    # TODO: Documentame
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()
        managers = RouteManagersRegistry.get_managers()

        async def custom_route_handler(
            request: Request, remaining_managers: List[Type[RouteManager]] = None
        ) -> Response:
            if remaining_managers is None:
                remaining_managers = managers.copy()

            if len(remaining_managers) > 0:
                manager_class = remaining_managers.pop()
                # Instantiate if it's not
                manager_instance = manager_class() if inspect.isclass(manager_class) else manager_class
                return await manager_instance.run(request, custom_route_handler, remaining_managers)
            else:
                return await original_route_handler(request)

        return custom_route_handler


class ManagedAPIRouter(APIRouter):
    # TODO: Documentame
    def __init__(self, *kargs: Any, **kwargs: Any) -> None:
        super().__init__(*kargs, **kwargs, route_class=ManagedRoute)
