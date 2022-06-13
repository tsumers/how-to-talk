import itertools

##### Define features and actions
COLORS = ["red", "green", "blue"]
SHAPES = ["square", "circle", "triangle"]
FEATURES = COLORS + SHAPES
ACTIONS = [{"color": action[0], "shape": action[1]} for action in itertools.product(COLORS, SHAPES)]

##### Define states
ALL_STATES = [list(l) for l in itertools.combinations(ACTIONS, 3)]


##### Define rewards
def generate_worlds_from_feature_values(features, possible_values):
    """Given lists of features and values, generate a dataframe with all possible feature-value combinations."""

    worlds_list = []

    for f in features:
        if not worlds_list:
            worlds_list = [{f: k} for k in possible_values]
        else:
            worlds_list = [dict(**w, **{f: k}) for w in worlds_list for k in possible_values]

    return worlds_list


ALL_REWARDS = generate_worlds_from_feature_values(SHAPES+COLORS, range(-2, 3))
TRUE_REWARDS = {"green": 2, "red": 0,  "blue": -2, "circle": 1, "triangle": 0, "square": -1}

##### Define utterances
DESCRIPTIONS = [{"type": "description", "feature": utt[0], "value": utt[1]}
                for utt in itertools.product(FEATURES, range(-2, 3))]

EXP_DESCRIPTIONS = [{"type": "description", "feature": utt[0], "value": utt[1]}
                    for utt in itertools.product(["green", "circle", "square", "blue"], [-2, -1, 1, 2])]


def generateInstructions(state):
    return [dict(action, **{"type": "instruction"}) for action in state]


def action_rewards_from_beliefs(action, beliefs):
    return beliefs[action["color"]] + beliefs[action["shape"]]


def utt_to_string(utt):
    if utt["type"] == "instruction":
        return f'instruction-{utt["color"]}-{utt["shape"]}'
    else:
        return f'description-{utt["feature"]}-{utt["value"]}'


def context_to_string(context):

    return ", ".join([a["shape"] + a["color"] for a in context])

INSTRUCTIONS = generateInstructions(ACTIONS)

ALL_UTTERANCES = DESCRIPTIONS + INSTRUCTIONS
EXP_UTTERANCES = EXP_DESCRIPTIONS + INSTRUCTIONS

UTTERANCES = {"all": ALL_UTTERANCES,
              "exp": EXP_UTTERANCES,
              "instructions": INSTRUCTIONS,
              "descriptions": DESCRIPTIONS}

