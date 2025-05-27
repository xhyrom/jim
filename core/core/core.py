from pathlib import Path

from fastapi import FastAPI
from uvicorn import Config as UvicornConfig
from uvicorn import Server

from .config import AppConfig
from .endpoints import router as api_router
from .intents.loader import IntentLoader
from .intents.processor import IntentProcessor


class Core:
    def __init__(self, config: AppConfig):
        self.app = FastAPI(title="title", description="desc", version="0.0.0")
        self.host = config.server.host
        self.port = config.server.port

        core_path = Path(__file__).parent.parent
        project_path = core_path.parent
        intents_path = project_path / "intents"

        self.intent_loader = IntentLoader(intents_path)
        self.intent_loader.load_all_intents()

        self.intent_processor = IntentProcessor(self.intent_loader, config)
        self.app.state.intent_processor = self.intent_processor

        self.setup_routes()

    def setup_routes(self):
        self.app.include_router(api_router)

    async def run(self):
        config = UvicornConfig(
            app=self.app, host=self.host, port=self.port, log_level="info"
        )
        server = Server(config)
        await server.serve()
