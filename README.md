# EXAFS Neo
#### Versions: 0.9.3
#### Last update: Oct 25, 2020

EXAFS Neo utilize Genetic algorithm in fitting Extended X-ray absorption fine structure(EXAFS).

## Pre-requisites
It is highly recommend to utilize `anaconda` or `pipx` package managers to prevent unforseen dependency conflicts. EXAFS Neo uses [`larch`](https://xraypy.github.io/xraylarch/) to process the x-ray spectrum.

  - Python: 3.x
  - Numpy: 1.17.2
  - Larch: >0.9.46
  - Matplotlib: 3.1.2

It is highly recommend to create a new environment in `anaconda` to run EXAFS Neo to prevent packages conflicts.

        conda create --name exafs python=3.7  numpy matplotlib pyqt
        conda activate exafs
        conda install -yc GSECARS xraylarch

## Installations
To install EXAFS Neo, simply clone the repo:

        git clone https://github.com/laumiulun/EXAFS-Neo-Public.git
        cd EXAFS-Neo-Public/
        python setup.py install

## Usage:
To run a sample test, make sure the enviornment is set correctly, and select a input file:
        #need data in path_files/Cu/path_75/
        exafs -i test/test.ini

## GUI
We also have provided a GUI for use in additions to our program, with additional helper script to facilitate post
analysis. To use the GUI:

        cd gui
        python XAFS_GUI.py
## Citation:

TBA
