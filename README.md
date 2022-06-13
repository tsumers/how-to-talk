# Data

Anonymized data from our behavioral experiment is provided in two `.csv` files:  

`final_exp_human_trials.csv` - contains the participant responses for the experiment.  
`final_human_exp_questions.csv` - contains freeform-text responses provided by participants at the end of the experiment.

The Jupyter notebook `Experiment-Analysis.ipynb` loads and explores both of these files. 

# Code

There are three codebases for this project: the analysis code (a Python repository and several Jupyter notebooks), the experiment code (Javascript), and a small R notebook used for statistical analyses of results.

## Python Analysis

The easiest way to explore the code is to look at the provided Jupyter Notebooks (`.pdf` versions are included for convenience). 

These consist of:  
`Speakers-and-Listeners`: the main notebook used to run the speaker / listener models; contains most of the analyses.  
`Experiment-Analysis`: loads the results from the behavioral experiment and visualizes participant utterance choices.  
`Social-and-Reinforcment-Learning`: used for the Thompson Sampling integration.  

### Running the code
Install the environment via Conda:

```conda env create -f environment.yml```

Run tests (from the main directory):

```python -m unittest```

Then you can launch a jupyter server to run the provided notebooks.

Note that the analysis caches pragmatic inference in order to speed up the analysis. Running it for the first time can take several hours, but the cache is too large to include in the supplemental zip file. The raw data can be instead downloaded at the following link

https://www.dropbox.com/s/j03e2yuj5h40vi9/neurips_supplement_data.zip?dl=0

The two folders, `cached_inference` and `cached_thompson_sampling`, should then be unzipped and placed in the `data/` directory. The Jupyter notebooks will read in the cached data from there.

## Javascript Experiment

The easiest way to look at the behavioral experiment is to visit the hosted version: http://pragmatic-bandits.herokuapp.com/. 

For completeness, the full (anonymized) JavaScript code is also provided.

## R analysis

Some of the statistical tests in the paper are performed in R. Data is exported from the Jupyter notebooks and then testing is done in the `analysis.Rmd` notebook.
