# EXAFS Neo
#### Versions: 0.9.9
#### Last update: May 15, 2023

<!-- ![example workflow](https://github.com/laumiulun/EXAFS_Neo/actions/workflows/<WORKFLOW_FILE>/badge.svg) -->

[![Test with Ubuntu, Miniconda](https://github.com/laumiulun/EXAFS_Neo/actions/workflows/test_ubuntu.yml/badge.svg?branch=unit_tests)](https://github.com/laumiulun/EXAFS_Neo/actions/workflows/test_ubuntu.yml)[![Test with Windows, Miniconda](https://github.com/laumiulun/EXAFS_Neo/actions/workflows/test_windows.yml/badge.svg?branch=unit_tests)](https://github.com/laumiulun/EXAFS_Neo/actions/workflows/test_windows.yml)

EXAFS Neo utilize Genetic algorithm in fitting Extended X-ray absorption fine structure(EXAFS).

## Prerequisites

It is highly recommend to utilize `anaconda` or `pip` package managers to prevent unforeseen dependency conflicts. EXAFS Neo uses [`larch`](https://xraypy.github.io/xraylarch/) to process the x-ray spectrum.

- Python: => 3.9
- Numpy: => 1.20
- Scipy: => 1.6
- Larch: > 0.9.47
- Matplotlib: > 3.0


It is highly recommend to create a new environment in `anaconda` to run EXAFS Neo to prevent packages conflicts. For `Windows` operating system, if you encounter a issue requiring "Microsoft C++ 14.0 or greater is needed", please download the tools at the following location [`C++ Tools`](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and make sure to select C++ build tools during installation process.

if you are on a Mac (either Intel or M1), you need to make sure that xcode command line tools is install, if not input this command into terminal:

        xcode-select --install

## Dependencies

EXAFS Neo requires the following dependencies to run:

        # Create new anaconda environment
        conda create -y --name exafs python=>3.9.10
        conda activate exafs
        conda install -y "numpy=>1.20" "scipy=>1.6" "matplotlib=>3.0" scikit-learn pandas
        conda install -y -c conda-forge wxpython pymatgen tomopy pycifrw
        pip install xraylarch


## Installations
To install EXAFS Neo, simply clone the repo:

        git clone https://github.com/laumiulun/EXAFS-Neo-Public.git
        cd EXAFS-Neo-Public/
        git clone https://github.com/laumiulun/EXAFS-Neo-Public.git
        cd EXAFS-Neo-Public/
        python setup.py install

## Usage
To run a sample test, make sure the environment is set correctly, and select a input file:

        exafs -i test/test.ini

The datafile requires header contain at least either a combination of (k, chi) or (energy, mu). It also requires a minimum of one newline for it to work correctly. Examples of the correct headers are as follows:

        #---------------------------------------------------------------------
        #  energy mu Io It Iref

        #---------------------------------------------------------------------
        #  k chi chik chik2 chik3 win energy

## Self adsorption correction:
EXAFS also provides a internal option to perform self-adsorption on the sample file using Booth et al correction. This is performed using git submodules:

        git submodule update --init --recursive
        cd contrib/sabcor/
        make

## Update
EXAFS Neo is under active development, to update the code after pulling from the repository:

        git pull --rebase
        python setup.py install


## GUI
We also have provided a GUI for use in additions to our program, with additional helper script to facilitate post-analysis. To use the GUI:

        cd gui/
        python XAFS_GUI.py


## Video Demonstrations
You can see a list of video demonstrations of the EXAFS Neo package presented, future presentation related to this software will be posted as they are available

<!-- - https://www.youtube.com/playlist?list=PLqZCvArs4yF8IrREQ3AzZJX2N-IRAPEmy [Aug 23,2021] (IIT EXAFS Workshop 2021)
- https://youtu.be/KwhItvwhapg [Feb 15, 2021] (University of Washington)
- https://youtu.be/jqISqq_FFR8 [Dec 10, 2020] (Canadian Light Source) -->

- [Demonstration Videos From IIT EXAFS Workshop 2021](https://www.youtube.com/playlist?list=PLqZCvArs4yF8IrREQ3AzZJX2N-IRAPEmy) (Aug 23,2021)
- [University of Washington](https://youtu.be/KwhItvwhapg) (Feb 15, 2021)
- [Canadian Light Source](https://youtu.be/jqISqq_FFR8) (Dec 10, 2020)

## Citation

Jeff Terry, Miu Lun Lau, Jiateng Sun, Chang Xu, Bryan Hendricks, Julia Kise, Mrinalini Lnu, Sanchayni Bagade, Shail Shah, Priyanka Makhijani, Adithya Karantha, Travis Boltz, Max Oellien, Matthew Adas, Shlomo Argamon, Min Long, and Donna Post Guillen, “Analysis of Extended X-ray Absorption Fine Structure (EXAFS) Data Using Artificial Intelligence Techniques,” Applied Surface Science 547, 149059 https://doi.org/10.1016/j.apsusc.2021.149059 (2021).
