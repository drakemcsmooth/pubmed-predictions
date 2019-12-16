from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, DefaultDict
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

from pubmed.abstract_lib import Abstract

import logging

log = logging.getLogger(__name__)


class AbstractProcessingException(ValueError):
    pass


class CachingPubMedProcessor:
    DEFAULT_CACHE_DIR = "abstract_cache"

    def __init__(self, cache_dir: Optional[str]):
        self.cache_dir = self._setup_cache_dir(cache_dir)
        self.processor = PubMedProcessor()
        self.cache = self._load_cache()

    def _setup_cache_dir(self, cache_dir: Optional[str]) -> str:
        """setup, if necessary, the directory to be used for cached abstracts"""
        if cache_dir is None:
            cache_dir = self.DEFAULT_CACHE_DIR

        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        return cache_dir

    def _load_cache(self) -> Dict[int, Abstract]:
        """load abstracts from the specified  directory"""
        # a generator containing all files ending in the Abstract's suffix
        path_gen = (str(s) for s in Path(self.cache_dir).iterdir() if s.suffix[1:] == Abstract.SUFFIX)

        # generate abstracts from the paths
        abstract_gen = (Abstract.load(path) for path in path_gen)

        # consume the chained generators into a dictionary
        return {abstract.pmid: abstract for abstract in abstract_gen}

    def _add_to_cache(self, pmid: int):
        """add the abstract of the specified article to the cache"""
        log.info("caching %s", pmid)
        abstract = self.processor.get_abstract(pmid)
        abstract.save(directory=self.cache_dir)
        self.cache[pmid] = abstract

    def get_abstract(self, pmid: int) -> Abstract:
        """get the abstract of the specified pmid"""
        if pmid not in self.cache:
            self._add_to_cache(pmid)
        return self.cache[pmid]


class PubMedProcessor:
    XML_KEY_ABSTRACT = "abstract"
    XML_KEY_ABSTRACT_TEXT = "abstracttext"
    XML_KEY_LABEL = "label"
    XML_KEY_CATEGORY = "nlmcategory"
    XML_KEY_CONTAINER = "pre"

    HTML_PARSER = "http.parser"
    XML_PARSER = "lxml"

    def __init__(self):
        self.base_url = "https://www.ncbi.nlm.nih.gov/pubmed/{pmid}?report=xml&format=text"

    def _get_url(self, pmid: int) -> str:
        return self.base_url.format(pmid=str(pmid))

    def get_xml_from_url(self, pmid: int) -> str:
        url = self._get_url(pmid)

        log.info("retrieving url: %s", url)
        response = requests.get(url)

        # raise an error, if one occurred
        response.raise_for_status()

        return response.text

    def create_abstract_from_xml(self, pmid: int, xml: str) -> Abstract:
        default_category = Abstract.DEFAULT_CATEGORY

        # parse the structure that contains the XML of interest
        container = BeautifulSoup(xml, self.XML_PARSER).find(self.XML_KEY_CONTAINER)

        # parse the contents of the container to access the abstract
        document = BeautifulSoup(container.text, self.XML_PARSER)

        abstract = document.find(self.XML_KEY_ABSTRACT)
        if not abstract:
            raise AbstractProcessingException("no abstract found in article {}".format(pmid))

        entries = abstract.find_all(self.XML_KEY_ABSTRACT_TEXT)
        if not entries:
            raise AbstractProcessingException("no abstract entries in article {}".format(pmid))

        text_by_label: DefaultDict[str, str] = defaultdict(str)
        if len(entries) == 1:
            text_by_label[default_category] = entries[0].text

        else:
            for entry in entries:
                attrs = entry.attrs
                if self.XML_KEY_CATEGORY in attrs:
                    key = entry[self.XML_KEY_CATEGORY]
                elif self.XML_KEY_LABEL in attrs:
                    key = entry[self.XML_KEY_LABEL]
                else:
                    key = None

                # add a period to ease future parsing efforts
                period = "."
                text = entry.text
                if text[-1] != period:
                    text += " " + period

                text_by_label[default_category] += entry.text
                if key:
                    text_by_label[key.lower()] += text

        return Abstract(pmid=pmid, **text_by_label)

    def get_abstract(self, pmid: int) -> Abstract:
        return self.create_abstract_from_xml(
            pmid=pmid,
            xml=self.get_xml_from_url(pmid),
        )
