import json

import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal

class MultivariateNormal(object):

    def __init__(self, mean, covariance=None):
        self.mean = mean
        self.covariance = covariance
        self._mvn = None

    def __str__(self):

        return "Mean:\n{}\nCovariance:\n{}".format(self.mean, self.covariance)

    @classmethod
    def from_labels(cls, labels, mean, var):
        mean = pd.Series(data=mean, index=sorted(labels))
        covariance = np.identity(len(labels)) * var

        return cls(mean, covariance)

    @property
    def mvn(self):
        if self._mvn is None:
            self._mvn = multivariate_normal(self.mean, self.covariance)
        return self._mvn

    def update_from_observation(self, X, Y, precision, verbose=False):
        """Take a feature vector (X) and rewards (Y) with fixed precision and return posterior MVN."""

        observation_mean = X * Y

        posterior_precision = np.linalg.inv(self.covariance) + np.outer(X, X) * precision
        posterior_covariance = np.linalg.inv(posterior_precision)

        posterior_mean = posterior_covariance @ (np.linalg.inv(self.covariance) @ self.mean
                                                 + precision * observation_mean)

        if verbose:
            print("Prior mean: {}\n".format(self.mean.values))
            print("Observation mean: \n{}\n".format(observation_mean))
            print("Posterior Covariance: \n{}\n".format(posterior_covariance))
            print("Posterior mean: {}\n".format(posterior_mean))

        return MultivariateNormal(mean=pd.Series(posterior_mean, index=self.mean.index),
                                  covariance=posterior_covariance)

    def sample_beliefs(self, n=100, as_df=True):

        rvs = self.mvn.rvs(n)
        if n == 1:
            rvs = [rvs]

        if as_df:
            return pd.DataFrame.from_records(rvs, columns=self.mean.index.values)
        else:
            return rvs

    def pdf(self, hypothesis_dataframe):

        # Filter to only the relevant columns, in sorted order
        to_evaluate = hypothesis_dataframe[self.mean.index.values]

        return self.mvn.pdf(to_evaluate)

    def to_json(self):

        return json.dumps({"mean": self.mean.values.tolist(),
                           "covariance": self.covariance.tolist(),
                           "features": self.mean.index.tolist()})

    @classmethod
    def from_json(cls, data):

        mean = pd.Series(data=data["mean"], index=data["features"])
        covariance = np.array(data["covariance"])
        return cls(mean, covariance=covariance)


