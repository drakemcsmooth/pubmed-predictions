# README

## Environment
To setup the environment, clone the repository and execute the setup script:
```
git clone git@github.com:adamgerber/pubmed-predictions.git
cd pubmed-predictions
source setup.sh
```

## Usage

### Clustering unlabeled data

```
python scripts/predict.py cluster <datafile>
```
#### Example
```
python scripts/predict.py cluster data/pmids_test_set_unlabeled.txt
```

### Evaluate a clustering against labeled data

```
python scripts/predict.py cluster <datafile> --evaluate
```

#### Example
```
python scripts/predict.py cluster data/pmids_gold_set_labeled.txt --evaluate
```


## Discussion

### 1. Text Processing
PubMed abstracts contain a high concentration of unique domain terms, such as
proper nouns as identifiers of diseases (e.g., Turner's syndrome) and symbolic
sequences to indicate genotype (e.g., "+/+") or complex chemical processes.
It is in the remaining text of the abstract that the highest variance is found
in two categories:

#### 1. natural language text, which is frequently qualitative, and describes
motivations, ranges of difficulty, or the intended effects of the work.

#### 2. measurements and results, frequently quantitative, which describe
structured phenomena (e.g., the results of experiments) who signals are
orthogonal to the task at hand, that is, categorizing abstracts by a common
disease, as opposed to categorizing by how successful or how large a sample
was used or how a significant a result.


### 2. Similarity Metric
For each abstract, a unigram language model is created, which is constructed
to contain only domain terms and their frequency, along with lemmatized
versions. The similarity metric is simply a dot-product of the language models
of any two abstracts and expresses a notion of mutual concern over topics.
Sometimes called "document-distance".


### 3. Clustering Algorithm
Each abstract is associated with the abstract that, according to the notion of
maximum likelihood, is most likely to have generated it, excluding itself).
This clustering occurs in O(n²) time and O(n) space.

Applying the above similarity metric produces a directed-graph, which is
traversed, depth-first as a tree, via breaking of cycles, assigning children
to the cluster of their recently assigned ancestors, mirroring bottom-up
hierarchical agglomerative clustering.

In further work, a metric such as BIC might be used to determined if an
additional round of clustering is called for, by comparing existing clusters
to determine whether there is sufficient similarity for a union to occur,
without sacrifice to model fitness.


### 4. Necessary Parameters
The clustering is non-parametric in that no count is necessary, nor is any
threshold value required. Observation shows that clustering tends to involve
a "hub" abstract, which mostly strongly characterizes a particular disease;
this abstract is the best match for numerous abstracts, which are its children
in the assignment tree and are the first abstracts assigned to the "hub"
abstract's cluster.


### 5. Design Choices and Complexity
This clustering occurs in O(n²) time and O(n) space, as each pair of abstracts
is compared to obtain a best match.

#### filtering common words
To ensure that the language model consists of domain terms, a list of frequent
words is used to eliminate common terms. Sets that are too large can filter
out salient domain terms, so here the Brown corpus is used, which contains
56k english words.

#### lemmatization / stemming
Using WordNet lemmatization produced good results in practice, however the value
of the extra morphological insights from lemmatization (as opposed to stemming)
would need further evaluation. For example, stemming transforms "livebirths"
to "livebirth" but lemmatization does not.

#### data processing
To facilitate analysis, simple caching is used: abstracts that are requested from
PubMed are saved as HDF5 files in a specified cache directory and are loaded from
disk on subsequent runs. If the cache directory is deleted, it is simply rebuilt
on later runs.


### 6. Gold Set Performance
In the test set of 86 examples, only a single instance was clustered incorrectly
which indicates a precision of 98.8%.


### 7. Output
Please see the file `gold_standard_results.txt`, in this directory


### 8. 
This method performed well on the test set (the article it miscategorized has
affinity for several possible clusters) and on several curated development sets.

This method excels at dealing with different magnitudes of similarity, owing to
the method for propagating assignments. However, if greater control is desired,
for example, wanting several types of ocular disease to appear in a single
cluster rather than several highly focused categories, then the approach would
need to change to incorporate paramaters that can be tuned.

Also, as mentioned in the source code, if clusters are too fragmented, a second
pass could occur, in which clusters are merged according to a policy of
minimizing (or making uniform) the variance of each cluster's members.

#### Further work

As is typical, this approaches focuses on similarity, but it less sensitive to
dissimilarity. One extension might be to produce a language model expressing
that a set of terms is required or prohibited. For example, in analyzing the
language models of the current members of a cluster, future candidates might be
rejected based on whether they satisfy the threshold of the required terms
or whether they contain too great a representation of prohibited terms.
