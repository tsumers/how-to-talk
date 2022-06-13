import random

from multivariate_normal import MultivariateNormal
from scipy.stats import norm
from configuration import FEATURES, ALL_STATES, TRUE_REWARDS, ALL_REWARDS, action_rewards_from_beliefs, utt_to_string

import pandas as pd
import numpy as np
import math
import time


class LearnerAgent(object):
    """Individual learning agents: Thompson sampling with optional importance-sampling from utterance posterior."""

    def __init__(self, utterance_posterior=None, instruction=None,
                 noise_variance=1, min_importance_samples=100, prior_var=3):

        # Set "social prior" from pragmatic inference or description, if we got one
        self.min_importance_samples = min_importance_samples
        if utterance_posterior is None:
            self.utterance_posterior = None
        else:
            # Collapse posterior across horizons
            utterance_posterior = utterance_posterior[FEATURES + ["probability"]]
            utterance_posterior = utterance_posterior.groupby(FEATURES).sum().reset_index()
            self.utterance_posterior = utterance_posterior.set_index(FEATURES)

        # Set "default action" from instruction, if we got one
        self.instruction = instruction

        # Set observation noise
        self.noise_variance = noise_variance
        self.noise_distribution = norm(loc=0, scale=math.sqrt(noise_variance))

        # Maintain a list of beliefs and belief updates.
        prior = MultivariateNormal.from_labels(sorted(FEATURES), mean=0, var=prior_var)
        self._individual_learning_beliefs = []
        self._individual_learning_beliefs.append(prior)

    @classmethod
    def from_literal_utterance(cls, utterance, **kwargs):

        if utterance["type"] == "instruction":
            instruction = {key: value for key, value in utterance.items() if key in ["color", "shape"]}
            return cls(instruction=instruction, **kwargs)

        elif utterance["type"] == "description":
            # Generate all possible worlds, then filter to ones that are consistent with this utterance
            possible_worlds = pd.DataFrame(ALL_REWARDS)
            possible_worlds["consistent"] = possible_worlds[utterance["feature"]] == utterance["value"]

            # OLD method: hard-filter to worlds that are consistent.
            # Unfortunately *when the utterance is false* (e.g. circle is -1), this breaks with enough learning,
            # as the Gaussian likelihood will eventually become incompatible with the remaining worlds.
            # possible_worlds = possible_worlds[consistent_worlds]
            # possible_worlds["probability"] = 1 / len(possible_worlds)

            # NEW method: set very low probability to worlds that are not consistent
            possible_worlds["probability"] = possible_worlds.consistent.apply(lambda x: 1 if x else 1e-10)

            return cls(utterance_posterior=possible_worlds, **kwargs)

    def discrete_hypotheses_from_gaussian_posterior(self, min_samples):

        sample_multiple = 5
        attempt = 1

        rounded = pd.DataFrame()
        while len(rounded) < min_samples:

            # First, draw samples from our latest MVN distribution
            # This will return possible values as rows of a dataframe
            beliefs = self._individual_learning_beliefs[-1].sample_beliefs(n=min_samples * sample_multiple)

            # Round to ensure we get whole numbers
            rounded = beliefs.round()

            # Rejection step: drop any samples that fall outside range of acceptable values (abs == 2)
            rounded["acceptable"] = rounded.apply(lambda x: all(abs(v) <= 2 for v in x.values), axis=1)
            rounded = rounded[rounded.acceptable]

            # Very rarely, we can get into a weird belief state where we reject a ton of samples.
            # Increase the number and try again...
            if len(rounded) < min_samples:
                if attempt % 3 == 0:
                    acceptance_rate = len(rounded) / float(len(beliefs))
                    print(f'\t\t\tFailed sampling: attempt {attempt}, {len(rounded)}/{len(beliefs)}={round(acceptance_rate, 2)} acceptable.')
                attempt += 1
                sample_multiple *= 10

        return rounded

    def sample_reward_posterior(self, n=1):

        # No social posterior. Just sample from Gaussians and return.
        if self.utterance_posterior is None:
            hypotheses = self.discrete_hypotheses_from_gaussian_posterior(min_samples=n)
            return hypotheses.sample(n)

        # If we have a social posterior, we need to run importance sampling.
        hypotheses = self.discrete_hypotheses_from_gaussian_posterior(min_samples=self.min_importance_samples)

        hypotheses = hypotheses.merge(self.utterance_posterior, how='left',
                                      left_on=FEATURES,
                                      right_index=True)

        # Then draw samples according to the utterance probability.
        return hypotheses.sample(n=n, weights='probability', replace=True)

    def update_beliefs(self, action):

        # Feature vector should have 1 for the action's shape and color, 0 otherwise
        X = pd.Series(np.zeros(len(FEATURES)), index=sorted(FEATURES))
        X[action["color"]] = 1
        X[action["shape"]] = 1

        # Add noise to observation based on
        Y = TRUE_REWARDS[action["color"]] + TRUE_REWARDS[action["shape"]] + self.noise_distribution.rvs()

        new_beliefs = self._individual_learning_beliefs[-1].update_from_observation(X, Y,
                                                                                    precision=1/self.noise_variance)
        self._individual_learning_beliefs.append(new_beliefs)

    def optimal_choice(self, state, beliefs, instruction=None):
        """Choose the best action according to a provided belief about rewards."""

        # If we have an instruction, first check if that action exists in this state.
        if instruction is not None:
            matched_action = [a for a in state if a == self.instruction]

            # If the action exists, return it without considering beliefs at all.
            if matched_action:
                return matched_action[0]

        # State is a list of actions, so convert to a list of rewards under this belief
        rewards = [action_rewards_from_beliefs(a, beliefs) for a in state]

        # Then return the best action
        return state[np.argmax(rewards)]

    def future_rewards(self, beliefs, instruction=None):

        future_rewards = 0
        for state in ALL_STATES:
            action = self.optimal_choice(state, beliefs, instruction)
            future_rewards += action_rewards_from_beliefs(action, TRUE_REWARDS)
        future_rewards = future_rewards / len(ALL_STATES)

        return future_rewards

    def thompson_sampling_learning(self, n_trials=1):

        expected_value_beliefs = []

        for trial in range(1, n_trials + 1):

            # Draw a random state
            state = random.choice(ALL_STATES)

            # Get a set of beliefs for this trial
            belief_samples = self.sample_reward_posterior(n=100)
            thompson_sample = belief_samples.sample(1)

            # Act according to the Thompson sample
            chosen_action = self.optimal_choice(state, beliefs=thompson_sample, instruction=self.instruction)

            # Calculate regret
            optimal_action = self.optimal_choice(state, TRUE_REWARDS)
            optimal_reward = action_rewards_from_beliefs(optimal_action, TRUE_REWARDS)
            obtained_reward = action_rewards_from_beliefs(chosen_action, TRUE_REWARDS)
            regret = optimal_reward - obtained_reward

            # Calculate future rewards w.r.t. mean belief state, *not* Thompson sample
            mean_belief = belief_samples.mean()
            future_rewards = self.future_rewards(beliefs=mean_belief, instruction=self.instruction)
            expected_value_beliefs.append({"future_rewards": future_rewards,
                                           "regret": regret,
                                           "trial": trial,
                                           "noise_var": self.noise_variance,
                                           "min_importance_samples": self.min_importance_samples})

            # Update beliefs for next round
            self.update_beliefs(chosen_action)

        return pd.DataFrame(expected_value_beliefs)

    @classmethod
    def cache_pragmatic_thompson_sampling(cls, pragmatic_listener, utterance, state, horizons, prior_var=3, workerid=None,
                                          min_importance_samples=100, n_trials=25, n_iterations=500, verbose=True,
                                          unique_str=""):

        context_str = " ".join(f'{a["shape"]}-{a["color"]}' for a in state)
        if workerid is not None:
            context_str += f'-{workerid}'
        thompson_sampling_str = f'h:{n_trials},samples:{min_importance_samples},var:{prior_var}'

        cache_str = f'U:{utt_to_string(utterance)}-C:({context_str})-H:{horizons}-T:({thompson_sampling_str})-S:({pragmatic_listener.speaker})'

        cache_str += unique_str
        file_path = "data/cached_thompson_sampling/" + cache_str + ".parquet"

        try:
            df = pd.read_parquet(file_path)
            previous_iterations = df["iteration"].max()
        except FileNotFoundError:
            df = pd.DataFrame()
            previous_iterations = 0
            if verbose:
                print(f'\tNo cached TS simulations (looking for {n_iterations}).')

        if previous_iterations >= n_iterations:
            return df[df["iteration"] <= n_iterations]

        # If we're here, we need to run more iterations on this setup.

        if verbose:
            print(f'\tRetrieved {previous_iterations} previous TS simulations (looking for {n_iterations}).')

        # Generate a posterior, then marginalize over horizon to get the probability of different reward weights.
        posterior = pragmatic_listener.inference(utterance, state, horizon=horizons)

        results = []
        start_time_ms = round(time.time() * 1000)
        for i in range(previous_iterations + 1, n_iterations + 1):
            learner_agent = cls(utterance_posterior=posterior,
                                min_importance_samples=min_importance_samples,
                                prior_var=prior_var)

            iteration_results = learner_agent.thompson_sampling_learning(n_trials=n_trials)
            iteration_results["iteration"] = i
            results.append(iteration_results)

            if verbose and i % 10 == 0:
                end_time_ms = round(time.time() * 1000)
                n_seconds = (end_time_ms - start_time_ms) / 1000
                print(f'\t\tTS simulation {i} of {n_iterations}, (+{n_seconds} seconds).')

                start_time_ms = end_time_ms

        df = pd.concat([df] + results)
        df.to_parquet(file_path)

        return df

    @classmethod
    def cache_literal_thompson_sampling(cls, utterance, prior_var=3, unique_str="",
                                        min_importance_samples=100, n_trials=25, n_iterations=1000, verbose=False):

        thompson_sampling_str = f'h:{n_trials},samples:{min_importance_samples},var:{prior_var}'
        cache_str = f'U:{utt_to_string(utterance)}-T:({thompson_sampling_str})-v3'
        cache_str += unique_str
        file_path = "data/cached_thompson_sampling/" + cache_str + ".parquet"

        try:
            df = pd.read_parquet(file_path)
            previous_iterations = df["iteration"].max()

        except FileNotFoundError:
            df = pd.DataFrame()
            previous_iterations = 0
            if verbose:
                print(f'\tLiteral utterance not yet cached ({utt_to_string(utterance)}).')

        if previous_iterations >= n_iterations:
            return df[df["iteration"] <= n_iterations]

        # If we're here, we need to run more iterations on this setup.
        results = []
        for i in range(previous_iterations + 1, n_iterations + 1):
            start_time_ms = round(time.time() * 1000)
            learner_agent = cls.from_literal_utterance(utterance,
                                                       min_importance_samples=min_importance_samples,
                                                       prior_var=prior_var)
            iteration_results = learner_agent.thompson_sampling_learning(n_trials=n_trials)
            end_time_ms = round(time.time() * 1000)

            iteration_results["iteration"] = i
            results.append(iteration_results)

            if verbose and i % 50 == 0:
                n_seconds = (end_time_ms - start_time_ms) / 1000
                print(f'\tIteration {i} of {n_iterations}, took {n_seconds} seconds.')

        df = pd.concat([df] + results)
        df.to_parquet(file_path)

        return df

    @classmethod
    def cache_individual_thompson_sampling(cls, prior_var=3, n_trials=25, n_iterations=1000, verbose=False,
                                           unique_str=""):

        thompson_sampling_str = f'h:{n_trials},var:{prior_var}'
        cache_str = f'individual-T:({thompson_sampling_str})'
        cache_str += unique_str
        file_path = "data/cached_thompson_sampling/" + cache_str + ".parquet"

        try:
            df = pd.read_parquet(file_path)
            previous_iterations = df["iteration"].max()

        except FileNotFoundError:
            df = pd.DataFrame()
            previous_iterations = 0

        if previous_iterations >= n_iterations:
            return df[df["iteration"] <= n_iterations]

        # If we're here, we need to run more iterations on this setup.
        results = []
        for i in range(previous_iterations + 1, n_iterations + 1):
            start_time_ms = round(time.time() * 1000)
            learner_agent = cls(prior_var=prior_var)
            iteration_results = learner_agent.thompson_sampling_learning(n_trials=n_trials)
            end_time_ms = round(time.time() * 1000)

            iteration_results["iteration"] = i
            results.append(iteration_results)

            if verbose and i % 50 == 0:
                n_seconds = (end_time_ms - start_time_ms) / 1000
                print(f'\tIteration {i} of {n_iterations}, took {n_seconds} seconds.')

        df = pd.concat([df] + results)
        df.to_parquet(file_path)

        return df
