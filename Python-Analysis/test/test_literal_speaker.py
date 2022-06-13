import unittest

from literal_speaker import LiteralSpeaker
from literal_listener import StatelessLiteralListener

listener = StatelessLiteralListener(alphaL=3)

TEST_CONTEXT = [{'color': 'red', 'shape': 'circle'},
                {'color': 'red', 'shape': 'triangle'},
                {'color': 'blue', 'shape': 'square'}]

instruction_absent = {"type": "instruction", "color": "green", "shape": "circle"}
instruction_present = {"type": "instruction", "color": "red", "shape": "circle"}


class MyTestCase(unittest.TestCase):

    def test_instructions(self):

        speaker = LiteralSpeaker(listener=listener, utterances="instructions")

        prob_good_instruction = speaker.single_utterance_probability(instruction_present, TEST_CONTEXT)
        self.assertAlmostEqual(prob_good_instruction, 1, 3)

        prob_bad_instruction = speaker.single_utterance_probability(instruction_absent, TEST_CONTEXT)
        self.assertAlmostEqual(prob_bad_instruction, 0, 3)

    def test_descriptions(self):

        speaker = LiteralSpeaker(listener=listener, utterances="descriptions")
        blue_pos = {"type": "description", "feature": "blue", "value": 2}
        prob_blue_pos = speaker.single_utterance_probability(blue_pos, TEST_CONTEXT)

        blue_neg = {"type": "description", "feature": "blue", "value": -2}
        prob_blue_neg = speaker.single_utterance_probability(blue_neg, TEST_CONTEXT)

        # Should almost certainly not say blue is positive, and should be more willing to say blue is negative
        self.assertAlmostEqual(prob_blue_pos, 0, 2)
        self.assertGreater(prob_blue_neg, prob_blue_pos)

        # Blue and square should be equally likely
        square_neg = {"type": "description", "feature": "square", "value": -2}
        prob_square_neg = speaker.single_utterance_probability(square_neg, TEST_CONTEXT)
        self.assertAlmostEqual(prob_square_neg, prob_blue_neg)

        # probs = speaker.all_utterance_probabilities(TEST_CONTEXT)
        # df = pd.DataFrame(speaker.utterances)
        # df["probs"] = probs

    def test_instructions_horizons(self):

        speaker = LiteralSpeaker(listener=listener, utterances="instructions")
        green_circle = {"type": "instruction", "color": "green", "shape": "circle"}

        probs = []
        for h in [1, 2, 3, 4, 5]:
            prob = speaker.single_utterance_probability(green_circle, TEST_CONTEXT, horizon=h)
            probs.append(prob)

        # probability of issuing this utterance should increase monotonically
        for shorter, longer in zip(probs, probs[1:]):
            self.assertLess(shorter, longer)

    def test_speaker_alpha(self):

        instruction_present = {"type": "instruction", "color": "red", "shape": "circle"}

        high_alpha = LiteralSpeaker(listener=listener, utterances="instructions", alphaS=10)
        high_alpha_prob = high_alpha.single_utterance_probability(
            instruction_present, TEST_CONTEXT, horizon=1)

        low_alpha = LiteralSpeaker(listener=listener, utterances="instructions", alphaS=3)
        low_alpha_prob = low_alpha.single_utterance_probability(
            instruction_present, TEST_CONTEXT, horizon=1)

        self.assertGreater(high_alpha_prob, low_alpha_prob)

    def test_green_description_horizons(self):

        speaker = LiteralSpeaker(listener=listener, utterances='all')
        green_description = {"type": "description", "feature": "green", "value": 2}

        probs = []
        for h in [1, 2, 3, 4, 5, 10]:
            prob = speaker.single_utterance_probability(green_description, TEST_CONTEXT, horizon=h)
            probs.append(prob)

        # probability of issuing this utterance should increase monotonically
        for shorter, longer in zip(probs, probs[1:]):
            self.assertLess(shorter, longer)

    def test_all_utterances(self):

        speaker = LiteralSpeaker(listener=listener, utterances='all')
        speaker.all_utterance_probabilities(TEST_CONTEXT, horizon=1)



if __name__ == '__main__':
    unittest.main()