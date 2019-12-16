from pathlib import Path

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import EnglishStemmer
from nltk.corpus import brown as nltk_common_words

from pubmed.language_model_builder import LanguageModelBuilder
from pubmed.pubmed_extractor_lib import PubMedProcessor

import pytest

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


test_data_dir = Path(Path(__file__).absolute().parent.parent.absolute(), "data")


@pytest.mark.unittest
def test_token_processor_word_net():
    pmid = 26323199

    expected_terms = {
        "aortic",
        "bicommissural",
        "chromosomal",
        "coarctation",
        "cohort",
        "hypoplasia",
        "karyotype",
        "karyotype-confirmed",
        "livebirths",
        "mosaicism",
        "non-mosaic",
        "population-based",
        "prenatally",
        "syndrome-associated",
        "syndrome-related",
        "turner",
        "utah",
    }

    test_path = Path(test_data_dir, "{}.xml".format(pmid))

    xml = open(test_path).read()
    processor = PubMedProcessor()
    abstract = processor.create_abstract_from_xml(pmid, xml)

    lemmatize = WordNetLemmatizer().lemmatize
    filter_words = set(nltk_common_words.words())

    language_model_builder = LanguageModelBuilder(filter_words=filter_words, lemmatize=lemmatize)
    abstract.counts = language_model_builder.build_language_model(abstract)

    terms = set(abstract.counts.keys())

    missing_terms = expected_terms - terms
    unexpected_terms = terms - expected_terms

    assert not missing_terms, missing_terms
    assert not unexpected_terms, unexpected_terms


@pytest.mark.unittest
def test_token_processor_snowball():
    pmid = 26323199

    expected_terms = {
        "aortic",
        "bicommissur",
        "bicommissural",
        "chromosom",
        "chromosomal",
        "coarctat",
        "coarctation",
        "cohort",
        "hypoplasia",
        "karyotyp",
        "karyotype",
        "karyotype-confirm",
        "karyotype-confirmed",
        "livebirth",
        "livebirths",
        "mosaic",
        "mosaicism",
        "non-mosa",
        "non-mosaic",
        "prenat",
        "population-bas",
        "population-based",
        "prenatally",
        "syndrome-associ",
        "syndrome-associated",
        "syndrome-rel",
        "syndrome-related",
        "turner",
        "utah",
    }

    test_path = Path(test_data_dir, "{}.xml".format(pmid))

    xml = open(test_path).read()
    processor = PubMedProcessor()
    abstract = processor.create_abstract_from_xml(pmid, xml)

    lemmatize = EnglishStemmer().stem
    filter_words = set(nltk_common_words.words())

    language_model_builder = LanguageModelBuilder(filter_words=filter_words, lemmatize=lemmatize)
    abstract.counts = language_model_builder.build_language_model(abstract)

    terms = set(abstract.counts.keys())

    missing_terms = expected_terms - terms
    unexpected_terms = terms - expected_terms

    assert not missing_terms, missing_terms
    assert not unexpected_terms, unexpected_terms
