from fastapi import FastAPI
from uvicorn import Config, Server

from .endpoints import router as api_router


class Core:
    def __init__(self, host="0.0.0.0", port=8000):
        self.app = FastAPI(title="title", description="desc", version="0.0.0")
        self.host = host
        self.port = port

        self.setup_routes()

    def setup_routes(self):
        self.app.include_router(api_router)

    async def run(self):
        config = Config(app=self.app, host=self.host, port=self.port, log_level="info")
        server = Server(config)
        await server.serve()
