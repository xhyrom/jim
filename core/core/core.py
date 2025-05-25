from fastapi import FastAPI
from uvicorn import Config, Server
from pathlib import Path

from .endpoints import router as api_router
from .intents.loader import IntentLoader
from .intents.processor import IntentProcessor
from .intents.fallback import FallbackHandler


class Core:
    def __init__(self, host="0.0.0.0", port=31415):
        self.app = FastAPI(title="title", description="desc", version="0.0.0")
        self.host = host
        self.port = port

        core_path = Path(__file__).parent.parent
        project_path = core_path.parent
        intents_path = project_path / "intents"

        self.intent_loader = IntentLoader(intents_path)
        self.intent_loader.load_all_intents()

        self.intent_processor = IntentProcessor(self.intent_loader)
        self.app.state.intent_processor = self.intent_processor

        self.setup_routes()

    def setup_routes(self):
        self.app.include_router(api_router)

    async def run(self):
        config = Config(app=self.app, host=self.host, port=self.port, log_level="info")
        server = Server(config)
        await server.serve()
