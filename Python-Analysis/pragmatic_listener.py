from collections import defaultdict, Counter

import numpy as np
import pandas as pd

from base_listener import BaseListener
from configuration import ALL_STATES, ALL_REWARDS


class PragmaticListener(BaseListener):

    def __init__(self, speaker, alphaL=3, all_states=ALL_STATES, possible_rewards=ALL_REWARDS):

        self.speaker = speaker
        self.possible_rewards = possible_rewards

        super().__init__(alphaL, all_states)

    def inference(self, utt, context, horizon):

        if isinstance(horizon, list):
            return self.multihorizon_inference(utt, context, horizon)
        else:
            return self.single_horizon_inference(utt, context, horizon)

    def single_horizon_inference(self, utt, context, horizon):

        context_str = self._get_cache_key(utt, context, horizon)
        file_path = "data/cached_inference/" + context_str + ".parquet"

        try:
            df = pd.read_parquet(file_path)
        except FileNotFoundError:
            df = self._regenerate_posterior_beliefs_from_utterance(utt, context, horizon)
            df.to_parquet(file_path)

        normalizing_constant = df.likelihoods.sum()
        df["probability"] = df.likelihoods / normalizing_constant
        return df

    def multihorizon_inference(self, utt, context, horizons):

        horizon_posteriors = []
        for h in horizons:
            single_horizon_posterior = self.single_horizon_inference(utt, context, h)
            single_horizon_posterior['horizon'] = h
            horizon_posteriors.append(single_horizon_posterior)

        multihorizon_posterior = pd.concat(horizon_posteriors)

        normalizing_constant = multihorizon_posterior.likelihoods.sum()
        multihorizon_posterior["probability"] = multihorizon_posterior.likelihoods / normalizing_constant

        return multihorizon_posterior

    def _regenerate_posterior_beliefs_from_utterance(self, utt, context, horizon):
        """Given a context/utterance, return distribution over rewards."""

        likelihoods = [self.speaker.single_utterance_probability(utt, context, horizon=horizon, reward_weights=w)
                       for w in self.possible_rewards]

        df = pd.DataFrame.from_records(self.possible_rewards)
        df["likelihoods"] = likelihoods

        return df

    def point_estimate_from_posterior(self, posterior_belief_df):

        point_estimate = posterior_belief_df.multiply(posterior_belief_df["probability"], axis='index').apply(np.sum)
        point_estimate = point_estimate.reindex(["green", "circle", "red", "triangle", "square", "blue"])

        return point_estimate

    def _feature_counts_from_point_estimate(self, context, point_estimate, alphaL=None):

        feature_counts = defaultdict(int)
        probabilities = [self.prob_action_from_beliefs(a, context, point_estimate, alphaL=alphaL) for a in context]
        for a, prob in zip(context, probabilities):
            feature_counts[a["color"]] += prob
            feature_counts[a["shape"]] += prob

        return feature_counts

    def _point_estimate_from_utterance(self, utt, context, horizon):

        posterior = self.inference(utt, context, horizon=horizon)
        point_estimate = self.point_estimate_from_posterior(posterior)

        return point_estimate

    def _get_cache_key(self, utt, context, horizon, alphaL=None):

        cache_str = "H:{}-C:{}-U:{}-{}".format(horizon, context, utt, self.speaker)
        if alphaL is not None:
            cache_str += str(alphaL)
        return cache_str

    def present_feature_counts(self, utt, context, horizon=1):
        """The feature counts associated with hearing this utterance in this context."""

        point_estimate = self._point_estimate_from_utterance(utt, context, horizon)
        return self._feature_counts_from_point_estimate(context, point_estimate)

    def future_feature_counts(self, utt, context, horizon=1, alphaL=None):
        """The feature counts associated with hearing this utterance in this context."""

        str_key = self._get_cache_key(utt, context, horizon, alphaL)
        if self.CACHED_FEATURE_COUNTS.get(str_key) is None:
            point_estimate = self._point_estimate_from_utterance(utt, context, horizon)
            feature_counts = self.future_feature_counts_from_point_estimate(point_estimate, alphaL=alphaL)
            self.CACHED_FEATURE_COUNTS[str_key] = feature_counts

        return self.CACHED_FEATURE_COUNTS[str_key]

    def future_feature_counts_from_point_estimate(self, point_estimate, alphaL=None):

        feature_counts = [Counter(self._feature_counts_from_point_estimate(c, point_estimate, alphaL=alphaL)) for c in self.ALL_STATES]
        acc = Counter()
        for c in feature_counts:
            acc += c

        avg_feature_counts = {k: v / len(self.ALL_STATES) for k, v in acc.items()}

        return avg_feature_counts

    def future_rewards_from_point_estimate(self, point_estimate, rewards, alphaL=None):

        features = self.future_feature_counts_from_point_estimate(point_estimate, alphaL=alphaL)
        return self.feature_count_rewards(features, rewards)

    def present_rewards(self, utt, context, rewards, horizon=1):

        feature_counts = self.present_feature_counts(utt, context, horizon)
        return self.feature_count_rewards(feature_counts, rewards)

    def future_rewards(self, utt, context, rewards, horizon=1, alphaL=None):

        feature_counts = self.future_feature_counts(utt, context, horizon, alphaL=alphaL)
        return self.feature_count_rewards(feature_counts, rewards)
