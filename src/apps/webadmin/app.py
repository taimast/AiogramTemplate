from base64 import b64encode

from fastapi import FastAPI
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

app = FastAPI()


class AdminAuth(AuthenticationBackend):
    username: str = "admin"
    password: str = "admin"

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if username != self.username or password != self.password:
            return False
        # Validate username/password credentials
        # And update session
        # create token from username/password
        token = b64encode(f"{username}:{password}".encode()).decode()
        request.session.update({"token": token})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        if token != b64encode(f"{self.username}:{self.password}".encode()).decode():
            return False

        return True
