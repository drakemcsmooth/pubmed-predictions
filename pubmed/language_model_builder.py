from typing import Set, Optional, Callable
from collections import Counter

from pubmed.pubmed_extractor_lib import Abstract
from pubmed.token_processor_lib import TokenProcessor
from analysis.data_processing_utils import SPACE

import logging

log = logging.getLogger(__name__)


class LanguageModelBuilder:
    def __init__(self, filter_words: Set[str], lemmatize: Optional[Callable] = None):
        self.token_processor = TokenProcessor(
            filter_words=filter_words,
            lemmatize=lemmatize,
        )

    def build_language_model(self, abstract: Abstract) -> Counter:
        """Build a unigram language model from the text of the specified abstract"""
        text = abstract.fields[abstract.DEFAULT_CATEGORY]

        token_processor = self.token_processor

        counts = Counter()
        for token in text.split(SPACE):
            token_counts = token_processor.extract(token)
            counts.update(token_counts)

        return counts
