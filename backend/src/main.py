# /src/main.py

# Primary Components
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Internal Modules
from src.api.routes import router
from src.utils.config import load_config, setup_environment_variables
from src.agent.agent_handler import (
    get_agent_handler,
)  # Dependency function and AgentHandler for the application


# Load configuration and set up environment variables
config = load_config()
setup_environment_variables(config)


async def startup_event(app: FastAPI):
    """
    Actions to be performed when the application starts up.
    Currently initializes the AgentHandler. Extend this function if more startup logic is needed.
    """
    app.agent_instance = get_agent_handler()


async def shutdown_event():
    """
    Cleanup actions to be performed when the application shuts down.
    Extend this function if any cleanup logic for components like AgentHandler is required.
    """
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup_event(app)
    yield
    # Shutdown
    await shutdown_event()


# Initialize the FastAPI application
app = FastAPI(lifespan=lifespan)

# Include the API router
app.include_router(router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
