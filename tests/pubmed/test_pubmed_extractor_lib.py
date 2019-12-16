from pathlib import Path

from bs4 import BeautifulSoup

from pubmed.pubmed_extractor_lib import PubMedProcessor, Abstract

import pytest

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


test_data_dir = Path(Path(__file__).absolute().parent.parent.absolute(), "data")

pmid_26323199 = 26323199

expected_abstracts = {
    pmid_26323199: Abstract(
        pmid=pmid_26323199,
        text=(
            "To evaluate the frequency of Turner syndrome in a population-based, "
            "statewide cohort of girls with coarctation of the aorta."
            "The Utah Birth Defects Network was used to ascertain a cohort of girls "
            "between 1997 and 2011 with coarctation of the aorta. Livebirths with "
            "isolated coarctation of the aorta or transverse arch hypoplasia were "
            "included and patients with complex congenital heart disease not usually "
            "seen in Turner syndrome were excluded."
            "Of 244 girls with coarctation of the aorta, 77 patients were excluded, "
            "leaving a cohort of 167 girls; 86 patients (51%) had chromosomal studies "
            "and 21 (12.6%) were diagnosed with Turner syndrome. All patients were "
            "diagnosed within the first 4 months of life and 5 (24%) were diagnosed "
            "prenatally. Fifteen patients (71%) had Turner syndrome-related findings "
            "in addition to coarctation of the aorta. Girls with mosaicism were less "
            "likely to have Turner syndrome-associated findings (3/6 mosaic girls "
            "compared with 12/17 girls with non-mosaic 45,X). Twelve girls (57%) "
            "diagnosed with Turner syndrome also had a bicommissural aortic valve."
            "At least 12.6% of girls born with coarctation of the aorta have "
            "karyotype-confirmed Turner syndrome. Such a high frequency, combined "
            "with the clinical benefits of an early diagnosis, supports genetic "
            "screening for Turner syndrome in girls presenting with coarctation of "
            "the aorta."
        )
    )
}


@pytest.mark.unittest
def test_pubmed_xml_processor_url_creation():
    pmids = [12345]

    processor = PubMedProcessor()

    for pmid in pmids:
        expected_url = "https://www.ncbi.nlm.nih.gov/pubmed/" + str(pmid) + "?report=xml&format=text"
        assert processor._get_url(pmid) == expected_url


@pytest.mark.unittest
def test_pubmed_xml_processor_abstract_extractor():
    pmid = 26323199

    test_path = Path(test_data_dir, "{}.xml".format(pmid))
    xml_expected = open(test_path, "rb").read()
    text_expected = BeautifulSoup(xml_expected).text

    processor = PubMedProcessor()
    text_retrieved = BeautifulSoup(processor.get_xml_from_url(pmid)).text

    assert text_expected == text_retrieved


@pytest.mark.unittest
def test_pubmed_xml_processor_create_abstract():
    pmid = 26323199

    test_path = Path(test_data_dir, "{}.xml".format(pmid))

    xml = open(test_path).read()
    processor = PubMedProcessor()
    abstract = processor.create_abstract_from_xml(pmid, xml)

    expected_abstract = expected_abstracts[pmid]
    log.info("test: %s", abstract.text)

    assert abstract.text == expected_abstract.text


@pytest.mark.unittest
def test_pubmed_xml_processor_create_abstract_live():
    pmid = 26323199

    processor = PubMedProcessor()
    abstract = processor.get_abstract(pmid)

    expected_abstract = expected_abstracts[pmid]

    assert abstract.text == expected_abstract.text

