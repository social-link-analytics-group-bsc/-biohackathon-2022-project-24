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

As part of the BioHackathon Europe 2022, we here report our project on analysing the scientific literature to understand the sex balance in the articles published on EuropePMC, following last year's project on the same question applied on EGA and dbgap (cite).

Our goal is to develop a full pipeline to automate the process of information retrieval about sample and sex representation. To that purpose, we will:
* Collect a large dataset through their API
* Parse the relevant sections
* Extract the required information using Natural Language Processing

Then we plan to analyze the data by evaluating the relationship between the disclosure of sex and ratio of females/males with available variables (journal, field, etc.) and how this evolves through time.

# Methodology


## Collecting the data

We collected the data using the API of EuropePMC. To get an interesting set of data for our purpose we only asked for the articles that spoke about humans or homo sapiens. 

We also filtered by ... 

## Extracting the candidate sentences

Since we expected the relevant information to be located in the "Methods" section, we parsed those sections and focused on finding sentences with mentions of sex and numbers.
We extracted the candidate sentence by looking for the tokens "woman", "man", "women", "men", "female", "male", "females", and "males", and then checking if there was a number in a window of three tokens before and after the mention of sex.
From the XX articles we had collected, we encountered XX candidate sentences that potentially contained the information we were interested on. 

## Training a model to identify the numbers

Once having identified the candidate sentences it was necessary to identify which numbers did correspond to sex samples' amounts. 
Given the unstructured nature of language, it was needed to use a language model to extract this right. 
On first place, we needed annotated data, so we deployed a platform for this purpose, and crowed-sourced the annotation by asking the participants of Biohackaton 2022 to collaborate.
This shared effort resulted in over a thousand annotated sentences, from which we used 500 annotations for our training set, 100 for our development set and a 100 for the test set. 
We used this data to fine-tune the BERT-base language model. We trained for 5 epochs with a learning rate of 0.00005. 
The model obtained a precision of 87.1, a recall of 89.6 and an F1 of 88.3 in the test set.
We employed this model to automatically annotate the whole XX articles in our dataset. 
This resulted with XX articles containing information about the sex of the samples. 

## Analysis of the data

# Results

# Discussion

* We could suggest creating metadata for this kind of info


# Formatting

Please keep sections to a maximum of only two levels.

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
