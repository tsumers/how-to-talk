import math

from configuration import ALL_STATES, action_rewards_from_beliefs


class BaseListener(object):
    """Base class for listeners: action softmax and necessary methods."""

    def __init__(self, alphaL=3, all_states=ALL_STATES):

        self.alphaL = alphaL
        self.ALL_STATES = all_states
        self.CACHED_FEATURE_COUNTS = {}

    def present_feature_counts(self, utt, context):
        """The feature counts associated with hearing this utterance in this context."""

        raise NotImplementedError

    def future_feature_counts(self, utt, context):
        """The *future* feature counts associated with hearing this utterance in this context. """

        raise NotImplementedError

    def present_rewards(self, utt, context, rewards):

        raise NotImplementedError

    def future_rewards(self, utt, context, rewards):

        raise NotImplementedError

    def prob_action_from_beliefs(self, action, context, beliefs, alphaL=None):

        if alphaL is None:
            alphaL = self.alphaL

        this_logit = action_rewards_from_beliefs(action, beliefs) * alphaL
        other_rewards = [action_rewards_from_beliefs(a, beliefs) * alphaL for a in context]

        # Need to worry about underflow, but contexts are only 3 items so probably not a concern in practice
        other_logits = sum([math.exp(r) for r in other_rewards])
        return math.exp(this_logit) / other_logits

    @staticmethod
    def feature_count_rewards(feature_counts, rewards):

        return sum([feature_counts[k] * rewards[k] for k in feature_counts.keys()])
