# EXAFS Neo
#### Versions: 0.9.4
#### Last update: Jan 15, 2021

EXAFS Neo utilize Genetic algorithm in fitting Extended X-ray absorption fine structure(EXAFS).

## Prerequisites
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

        exafs -i test/test.ini

## Update:
EXAFS Neo is under active development, to update the code after pulling from the repository:

        git pull --rebase
        python setup.py install

## GUI
We also have provided a GUI for use in additions to our program, with additional helper script to facilitate post
analysis. To use the GUI:

        cd gui
        python XAFS_GUI.py

## Potential Errors
If you get an error message involving psutl, make sure you are in the right conda environment and reinstall psutl and xraylarch:

        conda activate exafs
        conda install psutl
        conda install -yc GSECARS xraylarch

## Video Demonstration
You can see a video demonstration of the EXAFS Neo package presented at the Canadian Light Source.
https://youtu.be/jqISqq_FFR8

## Citation:

Jeff Terry, Miu Lun Lau, Jiateng Sun, Chang Xu, Bryan Hendricks, Julia Kise, Mrinalini Lnu, Sanchayni Bagade, Shail Shah, Priyanka Makhijani, Adithya Karantha, Travis Boltz, Max Oellien, Matthew Adas, Shlomo Argamon, Min Long, and Donna Post Guillen, “Analysis of Extended X-ray Absorption Fine Structure (EXAFS) Data Using Artificial Intelligence Techniques,” Applied Surface Science 547 (2021) 149059 https://doi.org/10.1016/j.apsusc.2021.149059 .  


