from typing import Dict

from collections import Counter


class Cluster:
    def __init__(self, cluster_id):
        self.id = cluster_id
        self.counts = Counter()
        self.num_abstracts = 0

    def add_counts_from_abstract(self, abstract):
        self.num_abstracts += 1
        self.counts.update(abstract.counts)

    @property
    def normalized_counts(self) -> Dict[str, float]:
        num_abstracts = self.num_abstracts
        return {
            term: count / num_abstracts for term, count in self.counts.items()
        }

    def __repr__(self):
        return "<cluster {}>".format(self.id)
