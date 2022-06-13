import unittest
import pandas as pd

from literal_listener import StatelessLiteralListener
from pragmatic_listener import PragmaticListener
from literal_speaker import LiteralSpeaker

from configuration import ALL_REWARDS, TRUE_REWARDS

TEST_CONTEXT = [{'color': 'red', 'shape': 'circle'},
                {'color': 'red', 'shape': 'triangle'},
                {'color': 'blue', 'shape': 'square'},]

instruction_present = {"type": "instruction", "color": "red", "shape": "circle"}
instruction_absent = {"type": "instruction", "color": "green", "shape": "circle"}
description_circle = {"type": "description", "feature": "circle", "value": 2}
description_green = {"type": "description", "feature": "green", "value": 2}

l0 = StatelessLiteralListener()
s1 = LiteralSpeaker(l0)
l1 = PragmaticListener(s1)

h1_instruction = l1.single_horizon_inference(instruction_present, TEST_CONTEXT, horizon=1)
h1_instruction_high_alpha = l1.single_horizon_inference(instruction_present, TEST_CONTEXT, horizon=1)

h1_description = l1.single_horizon_inference(description_circle, TEST_CONTEXT, horizon=1)
h2_description = l1.single_horizon_inference(description_circle, TEST_CONTEXT, horizon=2)

class MyTestCase(unittest.TestCase):

    def test_pragmatic_posterior_instructions(self):

        self.assertEqual(len(h1_instruction), len(ALL_REWARDS))

        h1_point_estimate = l1.point_estimate_from_posterior(h1_instruction)
        self.assertGreater(h1_point_estimate["circle"], h1_point_estimate["triangle"])
        self.assertAlmostEqual(h1_point_estimate['green'], 0)

        h2_posterior = l1.single_horizon_inference(instruction_present, TEST_CONTEXT, horizon=2)
        self.assertEqual(len(h2_posterior), len(ALL_REWARDS))

        # We get some negative information: you're less likely to think green is good if you're not talking about it
        h2_point_estimate = l1.point_estimate_from_posterior(h2_posterior)
        self.assertLess(h2_point_estimate["green"], h1_point_estimate["green"])

    def test_pragmatic_posterior_descriptions(self):

        h1_circle_mle = l1.point_estimate_from_posterior(h1_description)
        self.assertGreater(h1_circle_mle['circle'], h1_circle_mle['red'])
        self.assertGreater(h1_circle_mle['circle'], h1_circle_mle['triangle'])
        self.assertAlmostEqual(h1_circle_mle['green'], 0)

    def test_pragmatic_horizons(self):

        # LONGER HORIZON --> should increase confidence that circle is good (not just a local correlation)
        h1_circle_mle = l1.point_estimate_from_posterior(h1_description)
        h2_circle_mle = l1.point_estimate_from_posterior(h2_description)
        self.assertGreater(h2_circle_mle['circle'], h1_circle_mle['circle'])

    def test_utterance_cache_stable(self):

        h2_description_regenerated = l1._regenerate_posterior_beliefs_from_utterance(description_circle,
                                                                                     TEST_CONTEXT,
                                                                                     horizon=2)

        feature_list = ['square', 'circle', 'triangle', 'red', 'green', 'blue']

        merged = pd.merge(h2_description, h2_description_regenerated, left_on=feature_list, right_on=feature_list)
        prob_diffs = merged.likelihoods_x - merged.likelihoods_y
        for diff in prob_diffs:
            self.assertAlmostEqual(diff, 0)

    def test_pragmatic_multihorizon(self):

        future_rewards_single_horizon = l1.future_rewards(description_green, TEST_CONTEXT,
                                                          TRUE_REWARDS, horizon=1)

        future_rewards_multihorizon = l1.future_rewards(description_green, TEST_CONTEXT,
                                                        TRUE_REWARDS, horizon=[1, 2])

        self.assertGreater(future_rewards_multihorizon, future_rewards_single_horizon)
        self.assertAlmostEqual(future_rewards_multihorizon, 1.314466, 2)
        self.assertAlmostEqual(future_rewards_single_horizon, 0, 1)

        # And we should be pretty sure that the speaker's horizon is 2.
        posterior = l1.inference(description_green, TEST_CONTEXT, horizon=[1, 2])
        prob_horizon_two = posterior[posterior.horizon == 2].probability.sum()
        self.assertGreater(prob_horizon_two, .90)


if __name__ == '__main__':
    unittest.main()