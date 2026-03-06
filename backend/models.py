from pydantic import BaseModel

class User(BaseModel):

    email: str
    password: str


class Login(BaseModel):

    email: str
    password: str


class Watchlist(BaseModel):

    email: str
    stock: str