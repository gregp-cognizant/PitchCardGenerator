from llama_index.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
    SummaryExtractor,
    # EntityExtractor,
    KeywordExtractor,
)
from llama_index.schema import MetadataMode
from llama_index.ingestion import IngestionPipeline
from llama_index.text_splitter import SentenceSplitter

from src.services.azure_llm_service import AzureLlmBuilder, LLmType


class MetadataIngestionPipeline:
    @staticmethod
    def build_pipeline(
        llm=None,
        llm_type=None,
        metadata_mode=MetadataMode.EMBED,
        keywords=6,
        questions=3,
        num_workers=4,
        summaries=None,
        text_splitter=None,
        extract_title=True,
        extract_keywords=True,
        extract_summary=True,
        extract_questions_answered=True,
        vector_store=None,
    ) -> IngestionPipeline:
        if llm is None:
            if llm_type is None:
                llm_type = LLmType.LLAMA_AZURE_OPENAI_GPT_35_TURBO
            llm = AzureLlmBuilder().get_llm(llm_type)
        if text_splitter is None:
            text_splitter = SentenceSplitter()
        transformations = []
        transformations.append(text_splitter)
        if extract_title:
            transformations.append(
                TitleExtractor(
                    llm=llm,
                    metadata_mode=metadata_mode,
                    num_workers=num_workers,
                )
            )
        if extract_keywords:
            transformations.append(
                KeywordExtractor(llm=llm, keywords=keywords, num_workers=num_workers)
            )
        if extract_summary:
            if summaries is None:
                summaries = ["prev", "self", "next"]
            transformations.append(
                SummaryExtractor(
                    summaries=summaries,
                    llm=llm,
                    num_workers=num_workers,
                )
            )
        if extract_questions_answered:
            transformations.append(
                QuestionsAnsweredExtractor(
                    questions=questions,
                    llm=llm,
                    metadata_mode=metadata_mode,
                    embedding_only=False,
                )
            )
        return IngestionPipeline(
            transformations=transformations, vector_store=vector_store
        )
