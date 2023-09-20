# Routes Manager for FastAPI

Manipulate requests before [FastAPI](https://github.com/tiangolo/fastapi) processes them (even before middlewares), and responses once finished.

## Installation

```console
$ pip install fastapi-routesmanager
```


## Example

Using example `HeadersLogger` from this package.

```python
from typing import Union

from fastapi import FastAPI

from fastapi_routesmanager import HeadersLogger, RouteManagersRegistry, ManagedAPIRouter
import logging

logging.basicConfig(level=logging.DEBUG)  # Needed to get DEBUG output

RouteManagersRegistry.register_route_manager(HeadersLogger)  # Register manager

app = FastAPI()

router = ManagedAPIRouter()


@router.get("/")  # Use router instead of app
def read_root():
    return {"Hello": "World"}


@router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


app.include_router(router)  # Include the router to the app

```

<details>
<summary>Or you can register multiple managers at once</summary>

```python
RouteManagersRegistry.register_route_managers([
    HeadersLogger,
    ExceptionLogger
])
```
</details>

### Run it

```console
$ uvicorn main:app --reload
```

### Check it

Browse to http://127.0.0.1:8000 and check the server console.
You should see something like this showing the headers

```console
# DEBUG:headers_logger:Requests headers: Headers({'host': 'localhost:8000', 'user-agent': 'Mozilla Firefox', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'accept-language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3', 'accept-encoding': 'gzip', 'dnt': '1', 'connection': 'keep-alive', 'upgrade-insecure-requests': '1', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none'})
# DEBUG:headers_logger:Response headers: MutableHeaders({'content-length': '17', 'content-type': 'application/json'})
# INFO:     127.0.0.1:49370 - "GET /1 HTTP/1.1" 200 OK
```

## Creating custom Manager

In order to create a custom manager you need to extend `RouteManager` and declare an `async def run(...)` method.

Within this method you can access the request, execute it and get the response.

```python
from fastapi_routesmanager import RouteManager
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, List, Type, Optional


class CustomManager(RouteManager):
    async def run(
            self,
            request: Request,
            call_next: Callable,
            remaining_managers: List[Type[RouteManager]],
    ) -> Optional[Response]:
        # This will run the request through FastAPI  
        response: Response = await call_next(request, remaining_managers)
        return response

```

In the `remaining_managers` list you will find all remaining managers to be run. You can modify this list to add or remove managers dynamically.
