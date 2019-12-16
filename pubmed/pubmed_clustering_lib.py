from typing import List, Set, Dict, Tuple, Deque, Optional
from collections import defaultdict, deque
from functools import partial

from nltk.stem import WordNetLemmatizer
from nltk.corpus import brown as nltk_filter_words
from pubmed.scorer_lib import SimpleAbstractScorer

from pubmed.abstract_lib import Abstract
from pubmed.cluster_lib import Cluster
from pubmed.language_model_builder import LanguageModelBuilder
from pubmed.scorer_lib import BaseScorer
from analysis.data_processing_utils import (
    DatasetDescriptor,
    get_abstracts,
    get_pmids_from_unlabeled_file,
    get_labeled_data,
)

import logging

log = logging.getLogger(__name__)


class PubMedTermBasedClusterer:
    def __init__(
        self, scorer: Optional[BaseScorer] = None, language_model_builder: Optional[LanguageModelBuilder] = None
    ):
        self.scorer = scorer or self._init_default_scorer()
        self.language_model_builder = language_model_builder or self._init_default_language_model_builder()

    @staticmethod
    def _init_default_scorer() -> BaseScorer:
        return SimpleAbstractScorer()

    @staticmethod
    def _init_default_language_model_builder() -> LanguageModelBuilder:
        filter_words = set(nltk_filter_words.words())
        lemmatize = WordNetLemmatizer().lemmatize
        return LanguageModelBuilder(filter_words=filter_words, lemmatize=lemmatize)

    def _process_assignments(self, abstracts: List[Abstract]) -> Tuple[List[Cluster], Dict[Abstract, Cluster]]:
        """build the tree of assignments then traverse the tree so that the clusters are inherited
        by descendants"""

        clusters: List[Cluster] = []
        cluster_by_abstract: Dict[Abstract, Cluster] = {}
        children_of: Dict[Abstract, Set[Abstract]] = defaultdict(set)

        # an agenda for handling unassigned abstracts
        agenda: Deque[Abstract] = deque()

        for abstract in abstracts:
            self._build_assignment_tree(
                abstract=abstract,
                abstracts=abstracts,
                clusters=clusters,
                cluster_by_abstract=cluster_by_abstract,
                children_of=children_of,
                agenda=agenda,
            )

        # traverse the tree, assigning children to the cluster of their parent
        self._traverse_assignment_tree(cluster_by_abstract=cluster_by_abstract, children_of=children_of, agenda=agenda)

        return clusters, cluster_by_abstract

    def _build_assignment_tree(
        self,
        abstract: Abstract,
        abstracts: List[Abstract],
        clusters: List[Cluster],
        cluster_by_abstract: Dict[Abstract, Cluster],
        children_of: Dict[Abstract, Set[Abstract]],
        agenda: Deque[Abstract],
    ):
        get_score = partial(self.scorer.get_score, target_abstract=abstract)

        # find the abstract with the highest similarity score to this abstract
        best_abstract, best_score = max(
            ((abstract_i, get_score(model_abstract=abstract_i)) for abstract_i in abstracts if abstract != abstract_i),
            key=lambda pair: pair[1],
        )

        # were these abstracts already associated?
        if best_abstract in children_of[abstract]:
            # if these abstracts are mutual "best matches", then use the previously
            # visited abstract as root node for the upcoming tree traversal...
            agenda.append(abstract)
            # ...and create the cluster to which all of this abstract's
            # descendants will be assigned
            cluster = Cluster(cluster_id=len(clusters))
            clusters.append(cluster)
            cluster_by_abstract[abstract] = cluster
        else:
            # if not, link them and move on
            children_of[best_abstract].add(abstract)

    def _traverse_assignment_tree(
        self,
        agenda: Deque[Abstract],
        cluster_by_abstract: Dict[Abstract, Cluster],
        children_of: Dict[Abstract, Set[Abstract]],
    ):
        """Traverse the tree, assigning children to the cluster of their descendant"""

        # keep track of abstracts processed to prevent cycles
        abstracts_processed: Set[Abstract] = set()

        while agenda:
            parent_abstract = agenda.popleft()

            # have we already seen this abstract?
            if parent_abstract in abstracts_processed:
                # if so, skip it
                log.info("cycle found, skipping: %s", parent_abstract)
                continue

            # if not, process it
            abstracts_processed.add(parent_abstract)
            cluster = cluster_by_abstract[parent_abstract]

            # add this node's counts
            # note: these cluster counts are not currently used
            cluster.add_counts_from_abstract(parent_abstract)

            # assign each child to the cluster of its parent, which is
            # guaranteed to have been assigned to the cluster of its parent
            for child_abstract in children_of[parent_abstract]:
                cluster_by_abstract[child_abstract] = cluster
                agenda.append(child_abstract)

    def assign_best_abstracts(self, abstracts: List[Abstract]) -> Tuple[List[Cluster], Dict[Abstract, Cluster]]:
        """Find the optimal cluster assignment for each abstract in O(n^2) time
        where `n` is the number of abstracts"""

        clusters, cluster_by_abstract = self._process_assignments(abstracts)

        for unassigned_abstract in set(abstracts) - set(cluster_by_abstract.keys()):
            log.warning("unassigned: %s", unassigned_abstract.pmid)
            cluster = Cluster(cluster_id=len(clusters))
            cluster_by_abstract[unassigned_abstract] = cluster

        return clusters, cluster_by_abstract

    def build_clusters(self, abstracts: List[Abstract]) -> List[Set[Abstract]]:
        """Assign abstracts to clusters

        If further testing shows that clusters are too fragmented, obtain the variance in
        similarity for each cluster and, starting with the largest cluster, check the members of
        smaller clusters (or perhaps the smaller clusters, themselves) to see if absorbing those
        clusters maintains the previous variance (or diminishes within some threshold)
        """
        clusters, cluster_by_abstract = self.assign_best_abstracts(abstracts)

        assignments = defaultdict(set)
        for abstract, cluster in cluster_by_abstract.items():
            assignments[cluster].add(abstract)

        return list(assignments.values())

    def _clusters_to_pmids(self, abstracts: List[Abstract]) -> List[Set[int]]:
        clusters = self.build_clusters(abstracts)
        return [{abstract.pmid for abstract in cluster} for cluster in clusters]

    def _build_abstracts_from_pmids(self, pmids: List[int]) -> List[Abstract]:
        """Use the language model builder to generate each abstract's language model"""
        abstracts = get_abstracts(pmids)
        for abstract in abstracts:
            abstract.counts = self.language_model_builder.build_language_model(abstract)
        return abstracts

    def predict_clusters(self, dataset: DatasetDescriptor) -> List[Set[int]]:
        """Cluster the provided articles given their abstracts"""
        return self._clusters_to_pmids(
            abstracts=self._build_abstracts_from_pmids(pmids=get_pmids_from_unlabeled_file(dataset))
        )

    def predict_clusters_and_evaluate(self, dataset: DatasetDescriptor) -> Tuple[List[Set[int]], List[Set[int]]]:
        """Cluster the provided articles given their abstracts and display them in the context
        of their intended groupings, with respect to the labels"""
        pmids, expected_assignments = get_labeled_data(dataset)

        predicted_assignments = self._clusters_to_pmids(abstracts=self._build_abstracts_from_pmids(pmids=pmids))

        return predicted_assignments, expected_assignments
