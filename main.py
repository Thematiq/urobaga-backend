
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from hackaton import websocket_router


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# app.mount('/static', StaticFiles(directory='static'), name='static')
app.include_router(websocket_router)