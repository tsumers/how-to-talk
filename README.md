## How to talk so your robot will learn: Instructions, descriptions, and pragmatics

<img align="right" src="https://github.com/tsumers/how-to-talk/blob/2ebd327f2e76b10341e380bccfe196095faf9757/Javascript-Experiment/static/images/mushroom-picker.jpg" width="500">

### Code

There are three codebases for this project: the analysis code (a Python repository and several Jupyter notebooks), the experiment code (Javascript), and a small R notebook used for statistical analyses of results.

#### Python Analysis

The easiest way to explore the code is to look at the provided Jupyter Notebooks (`.pdf` versions are included for convenience). 

These consist of:  
`Speakers-and-Listeners`: the main notebook used to run the speaker / listener models; contains most of the analyses.  
`Experiment-Analysis`: loads the results from the behavioral experiment and visualizes participant utterance choices.  
`Social-and-Reinforcment-Learning`: used for the Thompson Sampling integration.  

#### Running the code
Install the environment via Conda:

```conda env create -f environment.yml```

Run tests (from the main directory):

```python -m unittest```

Then you can launch a jupyter server to run the provided notebooks.

Note that the analysis caches pragmatic inference in order to speed up the analysis. Running it for the first time can take several hours. The raw data can be instead downloaded [here](https://www.dropbox.com/s/j03e2yuj5h40vi9/neurips_supplement_data.zip?dl=0). The two folders, `cached_inference` and `cached_thompson_sampling`, should then be unzipped and placed in the `data/` directory. The Jupyter notebooks will read in the cached data from there.

#### Javascript Experiment

The easiest way to look at the behavioral experiment is to visit the hosted version: http://pragmatic-bandits.herokuapp.com/. 

The full JavaScript code is provided for inspection.

#### R analysis

The statistical tests in the paper are performed in R. Data is exported from the Jupyter notebooks and then testing is done in the `analysis.Rmd` notebook.


### Data

Anonymized data from our behavioral experiment is provided in two `.csv` files:  

`final_exp_human_trials.csv` - contains the participant responses for the experiment.  
`final_human_exp_questions.csv` - contains freeform-text responses provided by participants at the end of the experiment.

The Jupyter notebook `Experiment-Analysis.ipynb` loads and explores both of these files. 
