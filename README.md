# EXAFS_GA
#### Versions: 0.7
#### Last update: May 21, 2020


EXAFS_GA utilize Genetic algorithm in fitting Extended X-ray absorption fine structure(EXAFS).

## Pre-requisites
Usage of GA is highly recommend to use `anaconda` or `pip` package managers. EXAFS_GA uses `larch` to process the x-ray spectrum.

  - Python: 3.x
  - Numpy: 1.17.2
  - Larch: >0.9.46
  - Matplotlib: 3.1.2

It is highly recommend to create a new environment in `anaconda` to run EXAFS_GA to prevent packages conflicts.

        conda create --name EXAFS numpy matplotlib pyqt
        conda install -yc GSECARS xraylarch

## Installations
To install EXAFS_GA, simply clone the repo:

        git clone https://github.com/laumiulun/EXAFS.git


## Usage:
To run a sample test, make sure the enviornment is set correctly, and select a input file:

        python exafs -i test/test.ini  


## Citation:

TBA
