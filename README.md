# The Pilot Edition of the Protein Engineering Tournament


[![CC BY 4.0][cc-by-shield]][cc-by]


[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg

This document serves as a guide to navigate the repository of data and resources compiled for the pilot Protein Engineering Tournament. Our aim is to build a transparent platform for fostering collaboration, evaluating progress, and establishing benchmarks in the field of protein engineering. The pilot tournament is structured into three  tracks: Zero-Shot in silico, Supervised in silico, and in vitro, each designed to explore different facets of protein engineering. Please note that all of the provided data, participant submissions, and analysis scripts can be found on our [GitHub repository](https://github.com/the-protein-engineering-tournament/pet-pilot-2023).

## Repository Structure Overview

#### Doc

- Compiled Abstracts PDF: A collection of abstracts authored by
  participants, detailing the methodologies applied in their
  research. This document offers insights into the thought processes
  and strategies employed across the tournament. Teams were invited,
  but not required, to submit an abstract on the methods they wished
  to disclose.
- A Figures/Tables Folder: containing the .png/.csv graphics for the
  results from the in silico and in vitro rounds, including individual
  event results and leader-boards.

### Tracks
- In Silico Zero-Shot: Focuses on predicting protein function without
  provided training data.
- In Silico Supervised: Focuses on prediction protein function with
  provided training data.
- In Vitro: Focuses on generating protein sequences to maximize a
  desired set of properties, followed by empirical testing in a
  laboratory to validate the predictions made by computational
  methods.

Each track is contained within its own dedicated folder. Within each track are associated Events, organized as sub-folders containing the following information:

### Individual event folder contents
#### All tracks contain

- README: An overview document providing additional details of the
  challenge problem given to the teams.
- Jupyter notebooks: for organizing data and creating summary plots
  and tables.
- Input Folder: Data obtained from elsewhere, e.g. original data or
  data submitted by the teams.
- Output Folder: Data resulting from analyzing and re-organizing data
  as defined in the associated jupyter notebooks.

#### And the different input folders contain


-  In Silico Zero-Shot Events
  - For these events you will find the self-titled evaluation datasets
    for each event enzyme, this includes the sequences provided to
    teams and the corresponding property measurements used to evaluate
    the teams' predictions.
  - Predictions Folder: Contains CSV files with the prediction
    results submitted by each team.
- In Silico Supervised Events
  - Training Data: Provided to participants in the in silico
    (supervised) round. The training data consists of known protein
    sequences and their associated properties.
  - Test Data: The evaluation data for each challenge, consisting of
    protein sequences and with their properties left blank for teams
    to predict.
  - Test Data (with values): The evaluation data for each challenge,
    consisting of protein sequences and with their properties filled
    in. This data was what teams’ predictions were evaluated against
    in the supervised round.
  - Predictions Folder: Contains CSV files with the prediction
    results submitted by each team.
- In Vitro Event
  - The alpha-amylase training dataset, which includes
    the enzyme sequences and the corresponding property measurements.
  - A Generations Folder is included, documenting the generated
    protein sequences submitted by each team.
  - The measurement data and supporting sequence annotation from the
    cloning and screening team.


## Environment for analysis

- Python 3.12
- Dependencies in requirements.in,
  [pip-compiled](https://github.com/jazzband/pip-tools/) to
  requirements.txt
