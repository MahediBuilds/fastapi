from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.testclient import TestClient
from inline_snapshot import snapshot


class KwargsResponse(Response):
    media_type = "text/plain"

    def __init__(self, content: Any = None, **kwargs: Any) -> None:
        super().__init__(content, **kwargs)


class InheritedKwargsResponse(KwargsResponse):
    media_type = "text/html"


class ArgsRedirectResponse(RedirectResponse):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class OptionalStatusJSONResponse(JSONResponse):
    def __init__(
        self, content: Any, status_code: int | None = None, **kwargs: Any
    ) -> None:
        super().__init__(content, status_code=status_code or 200, **kwargs)


app = FastAPI()


@app.get("/kwargs", response_class=KwargsResponse)
def kwargs_response():
    return "Hello World"


@app.get("/inherited", response_class=InheritedKwargsResponse)
def inherited_kwargs_response():
    return "<p>Hello World</p>"


@app.get("/redirect", response_class=ArgsRedirectResponse)
def redirect_response():
    return "/kwargs"


@app.get("/optional-status", response_class=OptionalStatusJSONResponse)
def optional_status_response():
    return {"message": "Hello World"}


client = TestClient(app)


def test_kwargs_response():
    response = client.get("/kwargs")
    assert response.status_code == 200, response.text
    assert response.text == "Hello World"


def test_inherited_kwargs_response():
    response = client.get("/inherited")
    assert response.status_code == 200, response.text
    assert response.text == "<p>Hello World</p>"


def test_redirect_response():
    response = client.get("/redirect", follow_redirects=False)
    assert response.status_code == 307, response.text
    assert response.headers["location"] == "/kwargs"


def test_optional_status_response():
    response = client.get("/optional-status")
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Hello World"}


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200, response.text
    assert response.json() == snapshot(
        {
            "openapi": "3.1.0",
            "info": {"title": "FastAPI", "version": "0.1.0"},
            "paths": {
                "/kwargs": {
                    "get": {
                        "summary": "Kwargs Response",
                        "operationId": "kwargs_response_kwargs_get",
                        "responses": {
                            "200": {
                                "description": "Successful Response",
                                "content": {
                                    "text/plain": {"schema": {"type": "string"}}
                                },
                            }
                        },
                    }
                },
                "/inherited": {
                    "get": {
                        "summary": "Inherited Kwargs Response",
                        "operationId": "inherited_kwargs_response_inherited_get",
                        "responses": {
                            "200": {
                                "description": "Successful Response",
                                "content": {
                                    "text/html": {"schema": {"type": "string"}}
                                },
                            }
                        },
                    }
                },
                "/redirect": {
                    "get": {
                        "summary": "Redirect Response",
                        "operationId": "redirect_response_redirect_get",
                        "responses": {"307": {"description": "Successful Response"}},
                    }
                },
                "/optional-status": {
                    "get": {
                        "summary": "Optional Status Response",
                        "operationId": "optional_status_response_optional_status_get",
                        "responses": {
                            "200": {
                                "description": "Successful Response",
                                "content": {"application/json": {"schema": {}}},
                            }
                        },
                    }
                },
            },
        }
    )
