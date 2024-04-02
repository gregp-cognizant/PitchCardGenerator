import os
from enum import Enum

import openai
from langchain_openai import AzureChatOpenAI, AzureOpenAI, AzureOpenAIEmbeddings
from llama_index.embeddings import LangchainEmbedding
from llama_index.llms import AzureOpenAI as LlamaAzureOpenAI

from src.utils.config import load_config

# https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/switching-endpoints


class LLmType(Enum):
    AZURE_OPENAI_GPT4 = "azure_openai_gpt4"
    AZURE_OPENAI_GPT4_32K = "azure_openai_gpt4_32k"
    AZURE_OPENAI_GPT_35_TURBO: str = "azure_openai_35_turbo"
    LLAMA_AZURE_OPENAI_GPT4 = "llama_azure_openai_gpt4"
    LLAMA_AZURE_OPENAI_GPT4_32K = "llama_azure_openai_gpt4_32k"
    LLAMA_AZURE_OPENAI_GPT_35_TURBO = "llama_azure_openai_35_turbo"
    AZURE_EMBEDDINGS: str = "azure_embeddings"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"


class LlmDeploymentConfig:
    model_name: str = "model_name"
    deployment_name: str = "deployment_name"


class AzureLlmBuilder:
    def __init__(self):
        self.llm = None
        self.CONFIG = load_config()
        self.azure_openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = self.CONFIG["OpenAI"]["openai_api_base"]
        self.openapi_type = self.CONFIG["OpenAI"]["openai_api_type"]
        self.openapi_type = "azure"

    def get_llm(
        self,
        llm_type: LLmType = LLmType.AZURE_OPENAI_GPT4,
        temperature: int = 0,
        max_tokens: int = 512,
    ):
        if llm_type == LLmType.AZURE_OPENAI_GPT_35_TURBO:
            return AzureOpenAI(
                model=self.CONFIG["OpenAI"]["text_summary_model"],
                openai_api_version=self.CONFIG["OpenAI"]["openai_api_version"],
                # openai_api_base=self.openai_api_base,
                azure_endpoint=self.azure_endpoint,
                deployment_name=self.CONFIG["OpenAI"]["text_summary_deployment_name"],
                openai_api_key=self.azure_openai_api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif llm_type == LLmType.AZURE_OPENAI_GPT4:
            return AzureChatOpenAI(
                model=self.CONFIG["OpenAI"]["model"],
                azure_endpoint=self.azure_endpoint,
                openai_api_key=self.azure_openai_api_key,
                openai_api_type=self.openapi_type,
                openai_api_version=self.CONFIG["OpenAI"]["openai_api_version"],
                deployment_name=self.CONFIG["OpenAI"]["deployment_name"],
                model_version=self.CONFIG["OpenAI"]["model_version"],
            )
        elif llm_type == LLmType.AZURE_OPENAI_GPT4_32K:
            return AzureChatOpenAI(
                model=self.CONFIG["OpenAI"]["model_32k"],
                azure_endpoint=self.azure_endpoint,
                openai_api_key=self.azure_openai_api_key,
                openai_api_type=self.openapi_type,
                openai_api_version=self.CONFIG["OpenAI"]["openai_api_version"],
                deployment_name=self.CONFIG["OpenAI"]["deployment_name_32k"],
                model_version=self.CONFIG["OpenAI"]["model_version"],
            )
        if llm_type == LLmType.LLAMA_AZURE_OPENAI_GPT_35_TURBO:
            return LlamaAzureOpenAI(
                model=self.CONFIG["OpenAI"]["text_summary_model"],
                azure_endpoint=self.CONFIG["OpenAI"]["openai_api_base"],
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                deployment_name=self.CONFIG["OpenAI"]["text_summary_deployment_name"],
                api_version=self.CONFIG["OpenAI"]["openai_api_version"],
            )
        elif llm_type == LLmType.LLAMA_AZURE_OPENAI_GPT4:
            return LlamaAzureOpenAI(
                model=self.CONFIG["OpenAI"]["model"],
                azure_endpoint=self.CONFIG["OpenAI"]["openai_api_base"],
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                deployment_name=self.CONFIG["OpenAI"]["deployment_name"],
                api_version=self.CONFIG["OpenAI"]["openai_api_version"],
            )
        elif llm_type == LLmType.LLAMA_AZURE_OPENAI_GPT4_32K:
            return LlamaAzureOpenAI(
                model=self.CONFIG["OpenAI"]["model_32k"],
                azure_endpoint=self.CONFIG["OpenAI"]["openai_api_base"],
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                deployment_name=self.CONFIG["OpenAI"]["deployment_name_32k"],
                api_version=self.CONFIG["OpenAI"]["openai_api_version"],
            )
        elif (
            llm_type == LLmType.AZURE_EMBEDDINGS
            or llm_type == LLmType.TEXT_EMBEDDING_ADA_002
        ):
            # Only for Azure OpenAI Embeddings we must rely on openai.api_key
            # Docs say that we should be able to pass the key as a parameter, but it doesn't work
            # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html?highlight=azureopenai
            # ToDo: Fix this so we can specify the key as a parameter like in other llm types.
            # For now this doesn't break anything, but if we want to support multiple llm services in the future this will be a problem
            # Langchain issue related: https://github.com/langchain-ai/langchain/issues/12959
            openai.api_key = self.azure_openai_api_key

            embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=self.azure_endpoint,
                azure_deployment=self.CONFIG["OpenAI"][
                    "embedding_model_deployment_name"
                ],
                openai_api_version=self.CONFIG["OpenAI"]["openai_api_version"],
                openai_api_key=self.azure_openai_api_key,
            )
            return LangchainEmbedding(embeddings)

        else:
            raise ValueError(f"Invalid Azure llm_type: {llm_type}")
