# EXAFS Neo
#### Versions: 0.9.6
#### Last update: Jul 28, 2021

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
        pip install .

## Usage:
To run a sample test, make sure the enviornment is set correctly, and select a input file:

        exafs -i test/test.ini

The datafile requires header contain at least either a combination of (k, chi) or (energy, mu). It also requires a minimum of one newline for it to work correctly. An example of the correct header is as follow:

        #---------------------------------------------------------------------
        #  k chi chik chik2 chik3 win energy

## Self adsorption correction:
EXAFS also provides a internal option to perform self-adsorption on the sample file using Booth et al correction. This is performed using git submodules:

        git submodule update --init --recursive
        cd contrib/sabcor/
        make 
## Update:
EXAFS Neo is under active development, to update the code after pulling from the repository:

        git pull --rebase
        pip install .


## GUI
We also have provided a GUI for use in additions to our program, with additional helper script to facilitate post-analysis. To use the GUI:

        cd gui
        python XAFS_GUI.py


## Potential Errors
If you get an error message involving psutl, make sure you are in the right conda environment and reinstall psutl and xraylarch:

        conda activate exafs
        conda install psutl
        conda install -yc GSECARS xraylarch

## Video Demonstration
You can see a list of video demonstrations of the EXAFS Neo package presented, future presentation related to this software will be posted as they are available

- https://youtu.be/KwhItvwhapg [Feb 15, 2021] (University of Washington)
- https://youtu.be/jqISqq_FFR8 [Dec 10, 2020] (Canadian Light Source)

## Citation:

Jeff Terry, Miu Lun Lau, Jiateng Sun, Chang Xu, Bryan Hendricks, Julia Kise, Mrinalini Lnu, Sanchayni Bagade, Shail Shah, Priyanka Makhijani, Adithya Karantha, Travis Boltz, Max Oellien, Matthew Adas, Shlomo Argamon, Min Long, and Donna Post Guillen, “Analysis of Extended X-ray Absorption Fine Structure (EXAFS) Data Using Artificial Intelligence Techniques,” Applied Surface Science 547, 149059 https://doi.org/10.1016/j.apsusc.2021.149059 (2021).
