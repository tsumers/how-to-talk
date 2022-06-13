PASSED_tourismQuiz = false
PASSED_colorQuiz = false
PASSED_textureQuiz = false
PASSED_specificMushroomQuiz = false
PASSED_instructQuiz = false
PASSED_teachQuiz = false
PASSED_patchQuiz = false

function quizBlock(jsPsych, participantCondition) {
    return {
        timeline: [
            {timeline: [conditionDependentTourismQuiz(participantCondition), sectionFeedbackPage(jsPsych)],
                conditional_function: function(){return !PASSED_tourismQuiz}},

            {timeline: [mushroomPatchQuiz(participantCondition), sectionFeedbackPage(jsPsych)],
                conditional_function: function(){return !PASSED_patchQuiz}},

            {timeline: [colorQuiz(), sectionFeedbackPage(jsPsych)],
                conditional_function: function(){return !PASSED_colorQuiz}},

            {timeline: [textureQuiz(), sectionFeedbackPage(jsPsych)],
                conditional_function: function(){return !PASSED_textureQuiz}},

            {timeline: [specificMushroomQuiz(), sectionFeedbackPage(jsPsych)],
                conditional_function: function(){return !PASSED_specificMushroomQuiz}},

            // {timeline: [instructQuiz(participantCondition), sectionFeedbackPage(jsPsych)],
            //     conditional_function: function(){return !PASSED_instructQuiz}},
            //
            // {timeline: [teachQuiz(participantCondition), sectionFeedbackPage(jsPsych)],
            //     conditional_function: function(){return !PASSED_teachQuiz}},

        ]
    }
}

function sectionFeedbackPage(jsPsych) { return {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){

        // Grab results from last page
        var last_trial_correct = jsPsych.data.get().last(1).values()[0].correct;
        var last_trial_count = jsPsych.data.get().last(1).values()[0].total;

        // Add to running count
        QUIZ_QUESTIONS_TOTAL += last_trial_count
        QUIZ_QUESTIONS_CORRECT += last_trial_correct

        let results_string = `<br>${last_trial_correct}/${last_trial_count} questions correct.<br><br>`
        if(last_trial_count === last_trial_correct) {
            return results_string + `<strong>Great job!</strong><br>You've passed that section of the test.<br><br>`
        }

        else return results_string + `You will need to re-take that section.<br><br>`
    },
    choices: ['Next']
}}

function quizGradingPage(jsPsych) { return {
    timeline: [{
        type: jsPsychHtmlButtonResponse,
        stimulus: function(){

            QUIZ_TRIES_REMAINING -= 1

            psiturk.recordUnstructuredData(`quizAttempt-${3-QUIZ_TRIES_REMAINING}`, JSON.stringify({
                "attempt": 3 - QUIZ_TRIES_REMAINING,
                "correct": QUIZ_QUESTIONS_CORRECT,
                "total": QUIZ_QUESTIONS_TOTAL}))

            if(QUIZ_QUESTIONS_TOTAL === QUIZ_QUESTIONS_CORRECT) {

                psiturk.recordUnstructuredData(`quizPassed`, JSON.stringify({
                    "attempt": 3 - QUIZ_TRIES_REMAINING,
                    "correct": QUIZ_QUESTIONS_CORRECT,
                    "total": QUIZ_QUESTIONS_TOTAL}))

                PASSED_QUIZ = true
                return `<h2>Congratulations!</h2>
                        You've passed the test and earned your license!<br>
                        <img src="/static/images/mushroom-basket.png" width=450px><br>
                        Click to start guiding tourists.<br><br>
                        `
                }

            if(QUIZ_TRIES_REMAINING === 0) {

                psiturk.recordUnstructuredData(`quizFailed`, JSON.stringify({
                    "attempt": 3 - QUIZ_TRIES_REMAINING,
                    "correct": QUIZ_QUESTIONS_CORRECT,
                    "total": QUIZ_QUESTIONS_TOTAL}))

                return `<br>Oh no! You did not pass the Tour Guide test. <br>
                        The experiment will now end. <br>
                        <br>
                        You will receive the base payment for participating.<br>`
            }
            else {
                return `<br>
                        Your final score was <strong>${QUIZ_QUESTIONS_CORRECT}/${QUIZ_QUESTIONS_TOTAL}</strong>. <br>
                        You have <strong>${QUIZ_TRIES_REMAINING} attempt(s) remaining.</strong> <br>
                        <br>
                        You'll only need to re-take the sections you failed. <br><br>
                        Click to review the instructions and try again!`
            }
        },
        choices: ["Continue"]
    }],
    on_finish: function() {

        QUIZ_QUESTIONS_TOTAL = 0
        QUIZ_QUESTIONS_CORRECT = 0

        if(!PASSED_QUIZ && QUIZ_TRIES_REMAINING === 0) {
            EXPERIMENT_COMPLETED = true
            jsPsych.endExperiment()
        }
    }
}}

function conditionDependentTourismQuiz(participantCondition){
    switch (participantCondition["objective"]) {
        case "utility":
            return objectiveTourismQuiz()
        case "belief":
            return objectiveTourismQuiz()
        case "ambiguous":
            return ambiguousTourismQuiz()
    }
}

function ambiguousTourismQuiz() {

    const edible_string = "They are edible"
    const objective_string = "Help tourists pick good mushrooms"
    const all_of_the_above = "All of the above"

    return {
        type: jsPsychSurveyMultiChoice,
        preamble: "<h2>Tour Guiding in the Forest</h2>",
        questions: [
            {
                prompt: "What is your job as a tour guide?",
                options: [
                    "Prevent tourists from trampling mushroom patches",
                    `${objective_string}`,
                    "Teach tourists about forest animals",
                    "Show tourists where to find mushrooms",],
                required: true,
                name: 'tour-guide-job'
            },
            {
                prompt: "What is true about all mushrooms?",
                options: [
                    "They are tasty",
                    `${edible_string}`,
                    "They are protected by law",
                    "They are spotted"
                ],
                required: true,
                name: 'mushroom-properties'
            },
            {
                prompt: "What should you consider when deciding what to say?",
                options: [
                    "Which mushrooms are tasty",
                    "The visible mushroom patch",
                    "Whether the tourist is visiting other patches",
                   `${all_of_the_above}`],
                required: true,
                name: 'what-to-say'
            }
        ],
        on_finish: function(data){

            // Score the response as correct or incorrect.
            data.quiz_name = "ambiguous_tourism_quiz"
            data.quiz_attempt = 3-QUIZ_TRIES_REMAINING

            data.total = 3
            data.correct = 0
            if (data.response['what-to-say'] === all_of_the_above) {
                data.correct += 1
            }
            if (data.response['mushroom-properties'] === edible_string) {
                data.correct += 1
            }
            if (data.response['tour-guide-job'] === objective_string) {
                data.correct += 1
            }
            if (data.total === data.correct) {PASSED_tourismQuiz = true}


        }
    }
}

function objectiveTourismQuiz() {
    return {
        type: jsPsychSurveyMultiChoice,
        preamble: "<h2>Your Responsibilities as a Tour Guide</h2>",
        questions: [
            {
                prompt: "What is your job as a tour guide?",
                options: [
                    "Prevent tourists from trampling mushroom patches",
                    `${TOUR_GUIDE_OBJECTIVE}`,
                    "Teach tourists about forest animals",
                    "Show tourists where to find mushrooms",],
                required: true,
                name: 'tour-guide-job'
            },
            {
                prompt: "Are tour guides allowed to lie about mushroom features?",
                options: [
                    `${LYING_ALLOWED_BELIEF}`,
                    `${LYING_ALLOWED_UTILITY}`],
                required: true,
                name: 'lying-allowed'
            },
            {
                prompt: "Does it matter which mushrooms tourists choose?",
                options: [
                    `${MUSHROOM_CHOICE_BELIEF}`,
                    `${MUSHROOM_CHOICE_UTILITY}`],
                required: true,
                name: 'mushroom-choice-important'
            }
        ],
        on_finish: function(data){

            data.quiz_name = "objective_tourism_quiz"
            data.quiz_attempt = 3-QUIZ_TRIES_REMAINING

            // Score the response as correct or incorrect.
            data.total = 3
            data.correct = 0
            if (data.response['mushroom-choice-important'] === `${MUSHROOM_CHOICE_ANSWER}`) {
                data.correct += 1
            }
            if (data.response['lying-allowed'] === `${LYING_ALLOWED_ANSWER}`) {
                data.correct += 1
            }
            if (data.response['tour-guide-job'] === `${TOUR_GUIDE_OBJECTIVE}`) {
                data.correct += 1
            }
            if (data.total === data.correct) {PASSED_tourismQuiz = true}

        }
    }
}

function colorQuiz() {return {
    type: jsPsychSurveyLikert,
    preamble: "<h2>Mushroom Features 1</h2>Indicate how much each feature is worth.",
    questions: [
        {
            prompt: markdown(`<span class='centered'>${cheatsheetFeatureToHTML("Red", false)}</span><br>${featureRandomization["Red"]}`),
            labels: ["-2", "-1", "0", "+1", "+2"],
            required: true,
            name: 'Red'
        },
        {
            prompt: markdown(`<span class='centered'>${cheatsheetFeatureToHTML("Green", false)}</span><br>${featureRandomization["Green"]}`),
            labels: ["-2", "-1", "0", "+1", "+2"],
            required: true,
            name: 'Green'
        },
        {
            prompt: markdown(`<span class='centered'>${cheatsheetFeatureToHTML("Blue", false)}</span><br>${featureRandomization["Blue"]}`),
            labels: ["-2", "-1", "0", "+1", "+2"],
            required: true,
            name: 'Blue'
        },
    ], randomize_question_order: true,
    on_finish: function(data){

        data.quiz_name = "color_quiz"
        data.quiz_attempt = 3-QUIZ_TRIES_REMAINING

        // Score the response as correct or incorrect.
        data.total = 3
        data.correct = 0

        // Note that the responses are coded by Likert scale 0-4, e.g. their *index* on the slider.
        if (data.response['Green'] === 4) { // 4 == "+2"
            data.correct += 1
        }
        if (data.response['Red'] === 2) {
            data.correct += 1
        }
        if (data.response['Blue'] === 0) {
            data.correct += 1
        }
        if (data.total === data.correct) {PASSED_colorQuiz = true}

    }
}}

function textureQuiz() {return {
    type: jsPsychSurveyLikert,
    preamble: "<h2>Mushroom Features 2</h2>Indicate how much each feature is worth.",
    questions: [
        {
            prompt: markdown(`<span class='centered'>${cheatsheetFeatureToHTML("Spotted", false)}</span><br>${featureRandomization["Spotted"]}`),
            labels: ["-2", "-1", "0", "+1", "+2"],
            required: true,
            name: 'Spotted'
        },
        {
            prompt: markdown(`<span class='centered'>${cheatsheetFeatureToHTML("Striped", false)}</span><br>${featureRandomization["Striped"]}`),
            labels: ["-2", "-1", "0", "+1", "+2"],
            required: true,
            name: 'Striped'
        },
        {
            prompt: markdown(`<span class='centered'>${cheatsheetFeatureToHTML("Solid", false)}</span><br>${featureRandomization["Solid"]}`),
            labels: ["-2", "-1", "0", "+1", "+2"],
            required: true,
            name: 'Solid'
        }
    ], randomize_question_order: true,
    on_finish: function(data){

        data.quiz_name = "texture_quiz"
        data.quiz_attempt = 3-QUIZ_TRIES_REMAINING

        // Score the response as correct or incorrect.
        data.total = 3
        data.correct = 0
        // Note that the responses are coded by Likert scale 0-4, e.g. their *index* on the slider.
        if (data.response['Spotted'] === 3) {
            data.correct += 1
        }
        if (data.response['Solid'] === 2) {
            data.correct += 1
        }
        if (data.response['Striped'] === 1) {
            data.correct += 1
        }

        if (data.total === data.correct) {PASSED_textureQuiz = true}
    }
}}

function instructQuiz() {

    mushroom_one = {"color": "Green", "texture": "Solid"}
    mushroom_two = {"color": "Blue", "texture": "Spotted"}
    mushroom_three = {"color": "Blue", "texture": "Solid"}
    choose_randomly = "She would choose randomly"

    return {
        type: jsPsychSurveyMultiChoice,
        preamble: `
            <h2>How Instructions Work</h2>
            <div class='center flex-person-wrap'>
            <img src="/static/images/people/Carla.png" width=100px>
            <p>
                Carla is visiting this mushroom patch. <br>
            </p>
          </div>
          <div class="center">
          ${patchListToHTML([[mushroom_one, mushroom_two, mushroom_three]], false, false)}<br>
          </div>
            
            <strong>Which mushroom would Carla most likely take if you said the following?</strong>`,
        questions: [
            {
                prompt: `"Take ${featureRandomization["Green"]} ${featureRandomization["Solid"]} mushrooms."`,
                options: [
                    `${featureRandomization["Green"]} ${featureRandomization["Solid"]}`,
                    `${featureRandomization["Blue"]} ${featureRandomization["Spotted"]}`,
                    `${featureRandomization["Blue"]} ${featureRandomization["Solid"]}`,
                    `${choose_randomly}`],
                required: true,
                name: 'green-solid'
            },
            {
                prompt: `"Take ${featureRandomization["Green"]} ${featureRandomization["Striped"]} mushrooms."`,
                options: [
                    `${featureRandomization["Green"]} ${featureRandomization["Solid"]}`,
                    `${featureRandomization["Blue"]} ${featureRandomization["Spotted"]}`,
                    `${featureRandomization["Blue"]} ${featureRandomization["Solid"]}`,
                    `${choose_randomly}`],
                required: true,
                name: 'green-striped-random'
            },
        ],
        on_finish: function(data){

            data.quiz_name = "instructions_quiz"
            data.quiz_attempt = 3-QUIZ_TRIES_REMAINING

            // Score the response as correct or incorrect.
            data.total = 2
            data.correct = 0
            if (data.response['green-solid'] === `${featureRandomization["Green"]} ${featureRandomization["Solid"]}`) {
                data.correct += 1
            }
            if (data.response['green-striped-random'] === `${choose_randomly}`) {
                data.correct += 1
            }
            if (data.total === data.correct) {PASSED_instructQuiz = true}

        }
    }
}

function teachQuiz() {

    mushroom_one = {"color": "Green", "texture": "Solid"}
    mushroom_two = {"color": "Blue", "texture": "Spotted"}
    mushroom_three = {"color": "Blue", "texture": "Solid"}
    choose_randomly = "She would choose randomly"

    return {
        type: jsPsychSurveyMultiChoice,
        preamble: `
            <h2>How Teaching Works</h2>
            <div class='center flex-person-wrap'>
            <img src="/static/images/people/Carla.png" width=100px>
            <p>
                Carla is visiting this mushroom patch. <br>
            </p>
          </div>
          <div class="center">
          ${patchListToHTML([[mushroom_one, mushroom_two, mushroom_three]], false, false)}<br>
          </div>
            
            <strong>Which mushroom would Carla most likely take if you said the following?</strong>`,
        questions: [
            {
                prompt: `"${featureRandomization["Green"]} is <strong>+2</strong>."`,
                options: [
                    `${featureRandomization["Green"]} ${featureRandomization["Solid"]}`,
                    `${featureRandomization["Blue"]} ${featureRandomization["Spotted"]}`,
                    `${featureRandomization["Blue"]} ${featureRandomization["Solid"]}`,
                    `${choose_randomly}`],
                required: true,
                name: 'green-plus-two'
            },
            {
                prompt: `"${featureRandomization["Blue"]} is <strong>-2</strong>."`,
                options: [
                    `${featureRandomization["Green"]} ${featureRandomization["Solid"]}`,
                    `${featureRandomization["Blue"]} ${featureRandomization["Spotted"]}`,
                    `${featureRandomization["Blue"]} ${featureRandomization["Solid"]}`,
                    `${choose_randomly}`],
                required: true,
                name: 'blue-minus-two'
            },
        ],
        on_finish: function(data){

            data.quiz_name = "descriptions_quiz"
            data.quiz_attempt = 3-QUIZ_TRIES_REMAINING

            // Score the response as correct or incorrect.
            data.total = 2
            data.correct = 0

            if (data.response['green-plus-two'] === `${featureRandomization["Green"]} ${featureRandomization["Solid"]}`) {
                data.correct += 1
            }
            if (data.response['blue-minus-two'] === `${featureRandomization["Green"]} ${featureRandomization["Solid"]}`) {
                data.correct += 1
            }
            if (data.total === data.correct) {PASSED_teachQuiz = true}

        }
    }
}

function specificMushroomQuiz() {
    return {
        type: jsPsychSurveyLikert,
        preamble: "<h2>Specific Mushrooms</h2>Indicate how much each mushroom is worth.",
        questions: [
            {
                prompt: markdown(`<span class='centered'>${mushroomToHTML({"color": "Blue", "texture": "Striped"}, true)}</span>`),
                labels: ["-3", "-2", "-1", "0", "1", "2", "3"],
                required: true,
                name: 'Blue-Striped'
            },
            {
                prompt: markdown(`<span class='centered'>${mushroomToHTML({"color": "Green", "texture": "Spotted"}, true)}</span>`),
                labels: ["-3", "-2", "-1", "0", "1", "2", "3"],
                required: true,
                name: 'Green-Spotted'
            },
            {
                prompt: markdown(`<span class='centered'>${mushroomToHTML({"color": "Red", "texture": "Solid"}, true)}</span>`),
                labels: ["-3", "-2", "-1", "0", "1", "2", "3"],
                required: true,
                name: 'Red-Solid'
            }
        ],
        randomize_question_order: true,
        on_finish: function(data){

            data.quiz_name = "specific_mushroom_quiz"
            data.quiz_attempt = 3-QUIZ_TRIES_REMAINING

            // Score the response as correct or incorrect.
            data.total = 3
            data.correct = 0
            if (data.response['Red-Solid'] === 3) {
                data.correct += 1
            }
            if (data.response['Green-Spotted'] === 6) {
                data.correct += 1
            }
            if (data.response['Blue-Striped'] === 0) {
                data.correct += 1
            }
            if (data.total === data.correct) {PASSED_specificMushroomQuiz = true}
        }
    }
}

function mushroomPatchQuiz(participantCondition) {
    return {
        type: jsPsychSurveyLikert,
        preamble: "<h2>Mushrom Patches</h2>",
        questions: [
            {
                prompt: MUSHROOM_PATCHES_QUESTION,
                labels: ["1", "2", "3", "4", "5"],
                required: true,
                name: 'patch-question'
            },
            {
                prompt: "How many mushrooms do tourists take per patch?",
                labels: ["1", "2", "3", "4", "5"],
                required: true,
                name: 'maximum-mushrooms-per-patch'
            },
        ],
        on_finish: function(data){

            data.quiz_name = "mushroom_patch_quiz"
            data.quiz_attempt = 3-QUIZ_TRIES_REMAINING

            // Score the response as correct or incorrect.
            data.total = 2
            data.correct = 0

            if (data.response['maximum-mushrooms-per-patch'] === 0) {
                data.correct += 1
            }

            if (participantCondition['horizon'] === 'ambiguous') {
                if (data.response['patch-question'] === 2) {
                    data.correct += 1
                }
            } else if (participantCondition['horizon'] === 'random') {

                // Answers are zero-indexed, so spot #3 is "max of 4"
                if (data.response['patch-question'] === 3) {
                    data.correct += 1
                }
            } else {
                if (data.response['patch-question'] === (participantCondition['horizon'] - 1)) {
                    data.correct += 1
                }
            }

            if (data.total === data.correct) {PASSED_patchQuiz = true}

        }
    }
}
