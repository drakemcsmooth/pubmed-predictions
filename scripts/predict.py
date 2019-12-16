from __future__ import absolute_import

from typing import Optional
from pathlib import Path
import click

from pubmed.pubmed_clustering_lib import PubMedTermBasedClusterer
from analysis.data_processing_utils import DatasetDescriptor, TAB
from scripts.display_utils import display_evaluation_output, display_predicted_clusters

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command("cluster")
@click.argument("data_file", nargs=1, type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option("--evaluate", is_flag=True, type=bool)
@click.option("--separator", default=TAB, help='Field separator (e.g., " " for a csv or "\\t" for a tsv.', type=str)
def cluster(data_file: str, evaluate: bool = False, separator: Optional[str] = None):

    data_descriptor = DatasetDescriptor(Path(data_file), separator=separator)

    clusterer = PubMedTermBasedClusterer(

    )

    if evaluate:
        predicted_clusters, expected_clusters = clusterer.predict_clusters_and_evaluate(data_descriptor)

        display_evaluation_output(predicted_clusters=predicted_clusters, expected_clusters=expected_clusters)

    else:
        predicted_clusters = clusterer.predict_clusters(data_descriptor)

        display_predicted_clusters(clusters=predicted_clusters)


if __name__ == "__main__":
    cli()
