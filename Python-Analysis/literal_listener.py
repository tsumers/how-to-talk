from collections import defaultdict, Counter

from base_listener import BaseListener
from configuration import SHAPES, COLORS


class StatelessLiteralListener(BaseListener):
    """The Stateless listener treats each new utterance as independent."""

    def __str__(self):

        return "alphaL:{}".format(self.alphaL)

    @staticmethod
    def _prob_action_from_instruction(action, context, instruction):

        instructed_action = {key: value for key, value in instruction.items() if key in ["color", "shape"]}
        matched_action = [a for a in context if a == instructed_action]

        # We can't find that action in the context, so return random choice
        if not matched_action:
            return 1 / len(context)

        # We found the action, and this is it-- take it.
        if action == matched_action[0]:
            return 1

        # We found the action, but this *isn't* it-- don't take it.
        return 0

    def _prob_action_from_description(self, action, context, description, alphaL=None):
        """Assumes symmetric prior, such that the value of any unknown feature is zero."""

        beliefs = {k: 0 for k in SHAPES + COLORS}
        beliefs[description['feature']] = description['value']

        return self.prob_action_from_beliefs(action, context, beliefs, alphaL=alphaL)

    def present_feature_counts(self, utt, context, alphaL=None):
        """The base case for all feature-count functions: obtain expected features for a local context."""

        key = str(context) + str(utt)
        if alphaL is not None:
            key += str(alphaL)

        if not self.CACHED_FEATURE_COUNTS.get(key):

            feature_counts = defaultdict(int)

            if utt["type"] == "instruction":
                probabilities = [self._prob_action_from_instruction(a, context, utt) for a in context]
            else:
                probabilities = [self._prob_action_from_description(a, context, utt, alphaL=alphaL) for a in context]

            for a, prob in zip(context, probabilities):
                feature_counts[a["color"]] += prob
                feature_counts[a["shape"]] += prob

            self.CACHED_FEATURE_COUNTS[key] = feature_counts

        return self.CACHED_FEATURE_COUNTS[key]

    def future_feature_counts(self, utt, context=None, alphaL=None):

        key = str(utt)
        if alphaL is not None:
            key += str(alphaL)

        if not self.CACHED_FEATURE_COUNTS.get(key):

            all_contexts = [Counter(self.present_feature_counts(utt, c, alphaL=alphaL)) for c in self.ALL_STATES]
            acc = Counter()
            for c in all_contexts:
                acc += c

            avg_feature_counts = {k: v / len(self.ALL_STATES) for k, v in acc.items()}

            self.CACHED_FEATURE_COUNTS[key] = avg_feature_counts

        return self.CACHED_FEATURE_COUNTS[key]

    def present_rewards(self, utt, context, rewards):
        """Main entry point for evaluating utterances in context-- auto-caches results."""

        features = self.present_feature_counts(utt, context)
        return self.feature_count_rewards(features, rewards)

    def future_rewards(self, utt, context, rewards, alphaL=None):

        features = self.future_feature_counts(utt, context, alphaL=alphaL)
        return self.feature_count_rewards(features, rewards)