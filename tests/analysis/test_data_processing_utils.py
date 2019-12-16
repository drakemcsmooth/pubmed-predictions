from pathlib import Path

from analysis.data_processing_utils import DatasetDescriptor, get_pmids_from_unlabeled_file, TAB

import pytest

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

data_dir = Path(Path(__file__).absolute().parent.parent.parent.absolute(), "data")


@pytest.mark.unittest
def test_get_pmids_from_file():
    expected_pmids = [
        8001324, 12598898, 14707528, 17047017, 17487218, 17708142, 20351703,
        20578946, 21263000, 21706501, 22011734, 22705998, 23121401, 23211900,
        23239255, 23788295, 24081994, 24311526, 24443022, 24555249, 24666534,
        24813698, 24931486, 24939608, 25517026, 25533182, 25669767, 25711197,
        25754283, 25911666, 26298398, 26306841, 26309352, 26323199, 26350976,
        26526396, 26566693, 26607862, 26642845, 26895074, 26908026, 27090893,
        27181042, 27343792, 27496117, 27638981, 27662508, 27724990, 27862906,
        27903974, 28211982, 28349385, 28383843, 28385916, 28403077, 28442527,
        28456931, 28580713, 28623644, 28627089, 28647950, 28696559, 28699072,
        28716062, 28720066, 28834269, 28837453, 28911804, 29060458, 29261648,
        29271604, 29279609, 29348408, 29379197, 29860495, 30418046, 30419062,
    ]
    dataset = DatasetDescriptor(Path(data_dir, "pmids_test_set_unlabeled.txt"), TAB)
    pmids = get_pmids_from_unlabeled_file(dataset)

    assert pmids == expected_pmids
