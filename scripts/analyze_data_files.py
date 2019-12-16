from typing import Optional, List

from pathlib import Path
from collections import Counter

from nltk.stem import WordNetLemmatizer
from nltk.corpus import brown as nltk_common_words

from pubmed.pubmed_extractor_lib import Abstract
from pubmed.token_processor_lib import TokenProcessor
from analysis.data_processing_utils import (
    DatasetDescriptor, data_dir, get_pmids_from_unlabeled_file, get_abstracts, DASH, SPACE, TAB,
)

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


dataset1 = DatasetDescriptor(Path(data_dir, "pmids_test_set_unlabeled.txt"), TAB)
dataset2 = DatasetDescriptor(Path(data_dir, "pmids_gold_set_unlabeled.txt"), TAB)
dataset3 = DatasetDescriptor(Path(data_dir, "pmids_gold_set_labeled.txt"), TAB)


def compile_text_from_abstracts(abstracts: List[Abstract]) -> str:
    return " ".join(abstract.text for abstract in abstracts)


def analyze(dataset: DatasetDescriptor, limit: Optional[int] = None):
    pmids = get_pmids_from_unlabeled_file(dataset)
    abstracts = get_abstracts(pmids, limit)

    lemmatize = WordNetLemmatizer().lemmatize
    filter_words = set(nltk_common_words.words())

    token_processor = TokenProcessor(filter_words=filter_words, lemmatize=lemmatize)
    corpus = compile_text_from_abstracts(abstracts)

    counts = Counter()
    for token in corpus.split(SPACE):
        token_counts = token_processor.extract(token)
        counts.update(token_counts)

    log.info("terms: %s", counts)

    terms = set(counts.keys())
    log.info("num acronyms: {}".format(len(terms)))

    lowercase_terms = {x.lower() for x in terms}
    log.info("num acronyms: {} unique".format(len(lowercase_terms)))
    log.info("       diffs: {}".format(terms - lowercase_terms))

    lowercase_nodash_terms = {x.replace(DASH, "") for x in terms}
    log.info("num acronyms: {} unique no-dash".format(len(lowercase_nodash_terms)))
    log.info("       diffs: {}".format(terms - lowercase_nodash_terms))
    log.info("       diffs: {}".format(lowercase_terms - lowercase_nodash_terms))


if __name__ == "__main__":
    analyze(dataset1)
