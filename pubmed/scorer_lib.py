from pubmed.pubmed_extractor_lib import Abstract

import logging

log = logging.getLogger(__name__)


class BaseScorer:
    def get_score(self, target_abstract: Abstract, model_abstract: Abstract) -> float:
        raise NotImplementedError()


class SimpleAbstractScorer(BaseScorer):
    def get_score(self, target_abstract: Abstract, model_abstract: Abstract) -> float:
        """Obtain the similarity score for the specified abstracts, setup as a strategy-pattern
        for easy experimentation with other scoring approaches"""
        return self.dot_product_score(
            target_abstract=target_abstract,
            model_abstract=model_abstract,
        )

    @classmethod
    def dot_product_score(cls, target_abstract: Abstract, model_abstract: Abstract) -> float:
        """For each term that appears in both abstracts, obtain the product of the occurrence count
        in each abstract. We use this as an indication of common topic, summing over these values
        as an the final abstract/abstract similarity score"""
        target_counts = target_abstract.counts
        model_counts = model_abstract.counts

        return sum(target_count * model_counts.get(term, 0) for term, target_count in target_counts.items())
