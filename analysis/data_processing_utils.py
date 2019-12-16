from typing import Optional, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path

from pubmed.pubmed_extractor_lib import (
    CachingPubMedProcessor, AbstractProcessingException, Abstract,
)

import logging

log = logging.getLogger(__name__)

DATA_DIR_NAME = "data"
DEFAULT_CACHEDIR_NAME = "cache"


data_dir = Path(Path(__file__).absolute().parent.parent.absolute(), DATA_DIR_NAME)

SPACE = " "
DASH = "-"
TAB = "\t"
SLASH = "/"


@dataclass
class DatasetDescriptor:
    path: Path
    separator: str = TAB


def get_pmids_from_unlabeled_file(
    dataset: DatasetDescriptor,
    separator: Optional[str] = SPACE,
) -> List[int]:
    """Extract PMIDs from a file"""
    with dataset.path.open() as f:
        rows = [
            row.strip().split(separator) for row in f
        ]

    return [int(row[0]) for row in rows if row]


def get_pmids_from_labeled_file(path: Path, separator: Optional[str] = SPACE) -> List[Tuple[int, str]]:
    """Extract PMIDs and labels from a file"""
    with path.open() as f:
        rows = [
            row.strip().split(separator) for row in f
        ]

    return [(int(row[0]), row[1]) for row in rows if row]


def get_labeled_data(dataset_descriptor: DatasetDescriptor) -> Tuple[List[int], List[Set[int]]]:
    """Extract PMIDs and labels from a file and create clusters from those assignments"""
    labeled_pmids = get_pmids_from_labeled_file(
        path=dataset_descriptor.path,
        separator=dataset_descriptor.separator,
    )

    # a lookup to handle mapping of existing labels and cluster assignment
    # of new labels
    id_by_label = {}

    pmid_clusters_by_label_id = defaultdict(set)
    pmids = []
    for pmid, label in labeled_pmids:
        pmids.append(pmid)

        # create a new id if this label is new, provide the next integer as the id
        label_id = id_by_label.setdefault(label, len(id_by_label))

        pmid_clusters_by_label_id[label_id].add(pmid)

    return pmids, list(pmid_clusters_by_label_id.values())


def get_abstracts(pmids: List[int], limit: Optional[int] = None) -> List[Abstract]:
    """Fetch abstract from PubMed"""
    processor = CachingPubMedProcessor(cache_dir=Path(data_dir, DEFAULT_CACHEDIR_NAME))

    abstracts = []
    missed_pmids = []
    for pmid in pmids[:limit]:
        try:
            abstract = processor.get_abstract(pmid)
            abstracts.append(abstract)
        except AbstractProcessingException as exc:
            missed_pmids.append(pmid)
            log.warning(exc)
    if missed_pmids:
        log.warning("missing articles %s", missed_pmids)

    return abstracts
