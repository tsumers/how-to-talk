import unittest

from literal_listener import StatelessLiteralListener

from configuration import TRUE_REWARDS

TEST_CONTEXT = [{'color': 'red', 'shape': 'circle'},
                {'color': 'red', 'shape': 'triangle'},
                {'color': 'blue', 'shape': 'square'},]

instruction_absent = {"type": "instruction", "color": "green", "shape": "circle"}
instruction_present = {"type": "instruction", "color": "red", "shape": "circle"}

class MyTestCase(unittest.TestCase):

    def test_literal_listener_instructions(self):

        listener = StatelessLiteralListener(alphaL=3)

        prob_red_circle = listener._prob_action_from_instruction(TEST_CONTEXT[0], TEST_CONTEXT, instruction_present)
        self.assertEqual(prob_red_circle, 1)

        prob_red_triangle = listener._prob_action_from_instruction(TEST_CONTEXT[1], TEST_CONTEXT, instruction_present)
        self.assertEqual(prob_red_triangle, 0)

        prob_red_circle = listener._prob_action_from_instruction(TEST_CONTEXT[0], TEST_CONTEXT, instruction_absent)
        self.assertEqual(prob_red_circle, 1/3)

    def test_literal_listener_descriptions(self):

        listener = StatelessLiteralListener(alphaL=3)
        description = {"type": "description", "feature": "red", "value": 1}

        prob_action_one = listener._prob_action_from_description(TEST_CONTEXT[0], TEST_CONTEXT, description)
        prob_action_two = listener._prob_action_from_description(TEST_CONTEXT[1], TEST_CONTEXT, description)
        prob_action_three = listener._prob_action_from_description(TEST_CONTEXT[2], TEST_CONTEXT, description)

        self.assertEqual(prob_action_one, prob_action_two)
        self.assertGreater(prob_action_one, prob_action_three)
        self.assertAlmostEqual(prob_action_one, 0.4878555511603684, places=5)

        high_alpha_listener = StatelessLiteralListener(alphaL=10)
        prob_action_three_high_alpha = high_alpha_listener._prob_action_from_description(TEST_CONTEXT[2], TEST_CONTEXT, description)
        self.assertGreater(prob_action_three, prob_action_three_high_alpha)

        description_circle = {"type": "description", "feature": "circle", "value": 1}
        prob_action_one = listener._prob_action_from_description(TEST_CONTEXT[0], TEST_CONTEXT, description_circle)
        self.assertAlmostEqual(prob_action_one,  0.9094429985127419, places=5)

    def test_literal_listener_present_features(self):

        listener = StatelessLiteralListener(alphaL=3)
        random_features = listener.present_feature_counts(instruction_absent, TEST_CONTEXT)
        self.assertEqual(random_features['red'], 2/3)
        self.assertEqual(random_features['circle'], 1/3)

        instructed_features = listener.present_feature_counts(instruction_present, TEST_CONTEXT)
        self.assertEqual(instructed_features['red'], 1)
        self.assertEqual(instructed_features['circle'], 1)

        description_circle = {"type": "description", "feature": "circle", "value": 1}
        description_features = listener.present_feature_counts(description_circle, TEST_CONTEXT)
        self.assertAlmostEqual(description_features['circle'], 0.9094429985127419)
        self.assertAlmostEqual(description_features['square'] + description_features['triangle'],
                               1-0.9094429985127419)

    def test_literal_listener_present_rewards(self):

        listener = StatelessLiteralListener(alphaL=3)

        good_instruction_rewards = listener.present_rewards(instruction_present, TEST_CONTEXT, TRUE_REWARDS)
        self.assertEqual(good_instruction_rewards, 1)

        bad_instruction_rewards = listener.present_rewards(instruction_absent, TEST_CONTEXT, TRUE_REWARDS)
        self.assertEqual(bad_instruction_rewards, -2/3)

        description_circle = {"type": "description", "feature": "circle", "value": 1}
        low_alpha_rewards = listener.present_rewards(description_circle, TEST_CONTEXT, TRUE_REWARDS)
        self.assertAlmostEqual(low_alpha_rewards, 0.7736074962818548)

        high_alpha_listener = StatelessLiteralListener(alphaL=10)
        high_alpha_rewards = high_alpha_listener.present_rewards(description_circle, TEST_CONTEXT, TRUE_REWARDS)
        self.assertGreater(high_alpha_rewards, low_alpha_rewards)

    def test_literal_listener_future_features(self):

        listener = StatelessLiteralListener(alphaL=3)
        green_circle_instruction = {"type": "instruction", "shape": "circle", "color": "green"}
        avg_features_instruction = listener.future_feature_counts(green_circle_instruction)
        self.assertAlmostEqual(avg_features_instruction['green'], .5)
        self.assertAlmostEqual(avg_features_instruction['blue'], .25)

        green_circle_description = {"type": "description", "feature": "green", "value": 2}
        avg_features_advice = listener.future_feature_counts(green_circle_description)
        self.assertAlmostEqual(avg_features_advice['green'], 0.75899680)
        self.assertAlmostEqual(avg_features_advice['blue'], 0.12050159731120035)

    def test_literal_listener_future_rewards(self):

        listener = StatelessLiteralListener(alphaL=3)

        green_circle_instruction = {"type": "instruction", "shape": "circle", "color": "green"}
        avg_features_instruction = listener.future_feature_counts(green_circle_instruction)
        future_rewards_instruction = listener.feature_count_rewards(avg_features_instruction, TRUE_REWARDS)
        self.assertEqual(future_rewards_instruction, .75)

        rewards = listener.future_rewards(green_circle_instruction, None, TRUE_REWARDS)
        self.assertEqual(future_rewards_instruction, rewards)

        green_circle_description = {"type": "description", "feature": "green", "value": 2}
        avg_features_advice = listener.future_feature_counts(green_circle_description)
        future_rewards_advice = listener.feature_count_rewards(avg_features_advice, TRUE_REWARDS)
        self.assertAlmostEqual(future_rewards_advice, 1.2769904161327992)

        rewards = listener.future_rewards(green_circle_description, None, TRUE_REWARDS)
        self.assertEqual(future_rewards_advice, rewards)


if __name__ == '__main__':
    unittest.main()