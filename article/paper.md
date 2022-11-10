---
title: 'Quantitative bias assessment in ELIXIR - EuropePMC biomedical publications resources'
title_short: 'BioHackEU22 #24: bias assessment'
tags:
  - bias
  - NLP
  - biology
  - sex
authors:
  - name: First Author
    affiliation: 1
  - name: Last Author
    orcid: 0000-0000-0000-0000
    affiliation: 2
affiliations:
  - name: First Affiliation
    index: 1
  - name: Second Affiliation
    index: 2
date: 8 November 2022
cito-bibliography: paper.bib
event: BH22EU
biohackathon_name: "BioHackathon Europe 2022"
biohackathon_url:   "https://biohackathon-europe.org/"
biohackathon_location: "Paris, France, 2022"
group: Project 24
# URL to project git repo --- should contain the actual paper.md:
git_url: https://github.com/social-link-analytics-group-bsc/biohackathon-2022-project-24
# This is the short authors description that is used at the
# bottom of the generated paper (typically the first two authors):
authors_short: First Author \emph{et al.}
---


# Introduction

As part of the BioHackathon Europe 2022, we here report our project on analysing the scientific literature to understand the sex balance in the articles published on EuropePMC, following last year project on the same question apply on EGA and dbgap (cite).

Our goal is to develop a full pipeline to automate the process of information retrieval about sample and sex representation. To that purpose, we will:
* Collect the full dataset
* Parse the relevant sections
* Extract the required information
* Write an analysis on the state of sex bias in biology research

# Methodology

Please keep sections to a maximum of only two levels.

## Collecting the data

## Extracting the candidate sentences

## Training a model to identify the numbers

### Data annotation

### Model training

### Model evaluation

## Analysis of the data

# Results

# Discussion

* We could suggest creating metadata for this kind of info


# Formatting

This document use Markdown and you can look at [this tutorial](https://www.markdowntutorial.com/).

## Tables and figures

Tables can be added in the following way, though alternatives are possible:

Table 1
| Header 1 | Header 2 |
| -------- | -------- |
| item 1 | item 2 |
| item 3 | item 4 |

Tables and figures should be given before they are mentioned in the main text.
A figure is added with:

![BioHackrXiv logo](./biohackrxiv.png)
 
Figure 1. The BioHackrXiv logo.

# Other main section on your manuscript level 1

Lists can be added with:

1. Item 1
2. Item 2

# Citation Typing Ontology annotation

You can use CiTO annotations, as explained in [this BioHackathon Europe 2021 write up](https://raw.githubusercontent.com/biohackrxiv/bhxiv-metadata/main/doc/elixir_biohackathon2021/paper.md) and [this CiTO Pilot](https://www.biomedcentral.com/collections/cito).
Using this template, you can cite an article and indicate why you cite that article, for instance DisGeNET-RDF [@citesAsAuthority:Queralt2016].

Possible CiTO typing annotation include:

* citesAsDataSource: when you point the reader to a source of data which may explain a claim
* usesDataFrom: when you reuse somehow (and elaborate on) the data in the cited entity
* usesMethodIn
* citesAsAuthority
* discusses
* extends
* agreesWith
* disagreesWith

...

## Acknowledgements

...

## References
