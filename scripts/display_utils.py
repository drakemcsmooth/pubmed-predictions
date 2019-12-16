from typing import List, Set, Dict, Any

import logging

log = logging.getLogger(__name__)


def display_evaluation_output(predicted_clusters: List[Set[int]], expected_clusters: List[Set[int]]):
    color_by_abstract = display_expected_clusters_for_evaluation(expected_clusters)
    display_predicted_clusters_for_evaluation(predicted_clusters, color_by_abstract)


def display_expected_clusters_for_evaluation(expected_clusters: List[Set[int]]) -> Dict[int, int]:
    # prefix to easily identify Expected clusters as opposed to Predicted
    prefix = "E"

    groups: List[str] = []
    color_by_abstract: Dict[int, int] = {}

    for i, group in enumerate(expected_clusters):
        for pmid in group:
            color_by_abstract[pmid] = i

        name = "{prefix}{group_id}".format(prefix=prefix, group_id=i)
        members = " ".join(color(i, pmid) for pmid in sorted(group))
        groups.append("  {name}: {members}".format(name=name, members=members))

    print("\n\nexpected_clusters:\n")
    print("\n".join(groups))

    return color_by_abstract


def display_predicted_clusters_for_evaluation(clusters: List[Set[int]], color_by_abstract: Dict[int, int]):
    # prefix to easily identify Predicted clusters as opposed to Expected
    prefix = "P"

    groups: List[str] = []
    for i, cluster in enumerate(clusters):
        name = "{prefix}{group_id}".format(prefix=prefix, group_id=i)
        members = " ".join(color(color_by_abstract[pmid], pmid) for pmid in sorted(cluster))
        groups.append("  {name}: {members}".format(name=name, members=members))

    print("\n\npredicted clusters:\n")
    print("\n".join(groups))


def display_predicted_clusters(clusters: List[Set[int]]):
    # prefix to easily identify Predicted clusters as opposed to Expected
    prefix = "P"

    groups: List[str] = []
    for i, cluster in enumerate(clusters):
        name = "{prefix}{group_id}".format(prefix=prefix, group_id=i)
        members = " ".join(str(pmid) for pmid in sorted(cluster))
        groups.append("  {name}: {members}".format(name=name, members=members))

    print("\npredicted clusters:\n")
    print("\n".join(groups))


def color(i: int, s: Any) -> str:
    code: int = 91 + i
    return "\033[{code}m {s}\033[00m".format(code=code, s=s)
