from pathlib import Path

from fastapi import FastAPI
from uvicorn import Config as UvicornConfig
from uvicorn import Server

from echo import create_echo

from .config import AppConfig
from .endpoints import router as api_router
from .handlers import HandlerRegistry


class Core:
    def __init__(self, config: AppConfig):
        self.app = FastAPI(
            title="Jim Core", description="Intent processing core", version="0.1.0"
        )
        self.host = config.server.host
        self.port = config.server.port

        core_path = Path(__file__).parent.parent
        project_path = core_path.parent
        intents_path = project_path / "intents"

        self.echo = create_echo(intents_path)

        self.handler_registry = HandlerRegistry()

        self.app.state.echo = self.echo
        self.app.state.config = config
        self.app.state.handler_registry = self.handler_registry

        self.setup_routes()

    def setup_routes(self):
        self.app.include_router(api_router)

    async def run(self):
        config = UvicornConfig(
            app=self.app, host=self.host, port=self.port, log_level="info"
        )
        server = Server(config)
        await server.serve()
