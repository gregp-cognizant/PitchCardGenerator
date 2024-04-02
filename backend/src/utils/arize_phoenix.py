import logging

from src.utils.config import load_config
from phoenix.trace.langchain import OpenInferenceTracer, LangChainInstrumentor
from phoenix.trace.exporter import HttpExporter
from phoenix.trace.llama_index import OpenInferenceTraceCallbackHandler


class ArizePhoenix:
    """
    ArizePhoenix is a class designed to manage the initialization and setup of the Arize Phoenix tracing system.
    The ArizePhoenix class is initialized without any parameters. The necessary configurations should be set externally in the appropriate config file.
    """

    def __init__(self):
        self.logger = self.setup_logger()
        self.CONFIG = self.load_configurations()
        self.PHOENIX_ENDPOINT = self.CONFIG["Phoenix"]["endpoint"]
        self.check_endpoint_config()
        self.exporter = HttpExporter(endpoint=self.PHOENIX_ENDPOINT)
        self.tracer = self.init_tracer()
        self.callback_handler = self.init_callback_handler()
        self.logger.info("ArizePhoenix initialized successfully")

    @staticmethod
    def setup_logger():
        return logging.getLogger(__name__)

    @staticmethod
    def load_configurations():
        return load_config()

    def check_endpoint_config(self):
        if not self.PHOENIX_ENDPOINT:
            self.logger.error("PHOENIX_ENDPOINT is not set in config")
            raise ValueError("PHOENIX_ENDPOINT is not set in config")

    def init_tracer(self):
        tracer = OpenInferenceTracer(exporter=self.exporter)
        LangChainInstrumentor(tracer).instrument()
        return tracer

    def init_callback_handler(self):
        return OpenInferenceTraceCallbackHandler(exporter=self.exporter)
