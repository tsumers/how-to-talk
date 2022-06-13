from scipy.special import softmax
from configuration import TRUE_REWARDS, UTTERANCES


class LiteralSpeaker(object):
    """The literal speaker contains and chooses utterances w.r.t. a literal listener."""

    def __init__(self, listener, alphaS=10, reward_weights=TRUE_REWARDS, utterances="all", lie_penalty=0):

        self.listener = listener
        self.alphaS = alphaS
        self.reward_weights = reward_weights
        self.utterances = utterances
        self.lie_penalty = lie_penalty

    def __str__(self):

        base_str = "utt:{}-alphaS:{}-{}".format(self.utterances, self.alphaS, str(self.listener))
        if self.lie_penalty != 0:
            base_str += f'lie-penalty:{self.lie_penalty}'
        return base_str

    def truth_value(self, utt, reward_weights=None):

        # Truth value only has meaning if the utterance is a description and the speaker is truthful
        if utt["type"] == "instruction" or self.lie_penalty == 0:
            return 0

        if reward_weights is None:
            reward_weights = self.reward_weights

        truthful = reward_weights[utt["feature"]] == utt["value"]
        if truthful:
            return 0
        else:
            return self.lie_penalty

    def all_utterance_probabilities(self, context, horizon=1, reward_weights=None):

        utterances = UTTERANCES[self.utterances]

        if reward_weights is None:
            reward_weights = self.reward_weights

        truth_rewards = [self.truth_value(utt, reward_weights) for utt in utterances]
        present_rewards = [self.listener.present_rewards(utt, context, reward_weights) for utt in utterances]
        future_rewards = [self.listener.future_rewards(utt, context, reward_weights) for utt in utterances]

        utterance_rewards = [t + (p + (horizon - 1) * f)/horizon for t, p, f in zip(truth_rewards,
                                                                                    present_rewards,
                                                                                    future_rewards)]

        return softmax([r * self.alphaS for r in utterance_rewards])

    def single_utterance_probability(self, utt, context, horizon=1, reward_weights=None):

        utterances = UTTERANCES[self.utterances]

        probabilities = self.all_utterance_probabilities(context, horizon=horizon, reward_weights=reward_weights)

        return probabilities[utterances.index(utt)]