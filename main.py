
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from hackaton import websocket_router


# Bruh


app = FastAPI()

@app.get("/", response_class=FileResponse)
async def root():
    return 'web/dist/index.html'

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

app.include_router(websocket_router)

# Static files have the least priority
app.mount('/', StaticFiles(directory='web/dist'), name='static')
