//////////////////
// Instructions //
//////////////////

function welcomeInstructions() {
    return {
        type: jsPsychHtmlButtonResponse,
        stimulus: `<img src="/static/images/fungal-forest.jpg" width=600px><h2>Welcome to the Forest of Fungi!</h2>`,
        choices: [`Enter the forest`]
    }
}


function instructionsBlock(repetition, participantCondition) {
    return {
        type: jsPsychInstructions,
        pages: [
            experimentStructureInstructions(),
            mushroomIntroInstructions(),

            mushroomFeatureInstructions(),
            mushroomActionInstructions(),
            patchInstructions(),

            tourGuideJobInstructions(),
            touristItineraryInstructions(),

            instructOrTeach(),
            instructionOrDescribeInstructions(),
            instructionOrDescribeInstructionsTwo(),

            studyHallInstructions(repetition),
        ].filter(n => n), // filter out empty pages if any of these functions return none
        show_clickable_nav: true,
    }
}

function experimentStructureInstructions() {
    return `
      <div class="text-left">
      <img style="float: right; margin: 0px 15px 15px 0px;" src="/static/images/mushroom-picker.jpg" width="300px" />

      <h2>Foraging for Fungi</h2>
      The Forest of Fungi&trade; is famous for its mushrooms. Tourists flock from all over to forage for them. <br><br>
      
      However, there are lots of mushrooms, and some are tastier than others!
      <br>
      <br>
      <h2>This Experiment</h2>
      You will play a <strong>tour guide</strong> at the Forest of Fungi&trade;. 
      <br>
      <br>
      <ul>
      <li>in the <strong>instructions</strong>, you will learn about the forest. </li>
      <li>if you pass the <strong>mushroom exam</strong>, you will earn your license. </li>
      <li>finally, as a <strong>licensed guide</strong>, you will advise tourists. </li>
      </ul>
      <br>
      </div>
      
      Next: begin learning about mushrooms!

    `}

function mushroomIntroInstructions() {
    return `<h2>Mushrooms: Good, Bad, or Bland?</h2><br>
      <div class="text-left">

      <img style="float: right; margin: 0px 15px 15px 0px;" src="/static/images/mushroom-intro-rainbow.png" width="300px" />

      <strong>All of the mushrooms are edible.</strong><br>
      None are poisonous.<br><br>
      
      However, not all taste good!
      <ul>
      <li>some are <strong>delicious</strong></li>
      <li>some are <strong>bitter</strong></li>
      <li>others are just <strong>bland</strong></li>
      </ul>
      <br><br><br>
      </div>
      
      Next: what makes mushrooms tasty (or not)...

    `}

function mushroomFeatureInstructions() {
    return `
      <h2>Mushroom Features</h2>
      Mushrooms come in three colors and three textures.<br>
      
      Each <strong>color</strong> or <strong>texture</strong> has a different tasty score!<br><br>
      
    <div class="row">
    <div class="col-sm-4"><span>${cheatsheetFeatureToHTML("Green")}</span></div>
    <div class="col-sm-4"><span>${cheatsheetFeatureToHTML("Red")}</span></div>
    <div class="col-sm-4"><span>${cheatsheetFeatureToHTML("Blue")}</span></div>
    </div>
    <div class="row">
    <div class="row"></div>
    <div class="col-sm-4"><span>${cheatsheetFeatureToHTML("Spotted")}</span></div>
    <div class="col-sm-4"><span>${cheatsheetFeatureToHTML("Solid")}</span></div>
    <div class="col-sm-4"><span>${cheatsheetFeatureToHTML("Striped")}</span></div>
    </div>
    
    <br>
    Take a moment to <strong>study these features</strong>.<br>
    You'll need to know them to earn your license!`}

function mushroomActionInstructions () {
    return `
    <h2>Mushrooms</h2>
    The <strong>tastiness</strong> of a mushroom is just the <strong>sum of its features</strong>.
    <br><br>    
    <div class="row display-flex-center">
    <div class="col-sm-3"><span>${cheatsheetFeatureToHTML("Green")}</span></div>
    <div class="col-sm-1"><span><p style="font-size: xxx-large">+</p></span></div>
    <div class="col-sm-3"><span>${cheatsheetFeatureToHTML("Striped")}</span></div>
    <div class="col-sm-2"><span><p style="font-size: xxx-large">=</p></span></div>
    ${cheatsheetMushroomToHTML({"color": "Green", "texture":"Striped"})}
    </div>
    This mushroom is <strong>tasty</strong>!<br><br>
        
    <div class="row display-flex-center">
    <div class="col-sm-3"><span>${cheatsheetFeatureToHTML("Blue")}</span></div>
    <div class="col-sm-1"><span><p style="font-size: xxx-large">+</p></span></div>
    <div class="col-sm-3"><span>${cheatsheetFeatureToHTML("Solid")}</span></div>
    <div class="col-sm-2"><span><p style="font-size: xxx-large">=</p></span></div>
    ${cheatsheetMushroomToHTML({"color": "Blue", "texture":"Solid"})}
    </div>
    This mushroom is <strong>bitter</strong>!
    <br><br>
    ${mushroomModal()}
    <br>
    <strong>Here's a handy summary of all mushrooms.</strong>
    <br>
    <br>
    `}

function patchInstructions() {
    return `
      <h2>Mushroom Patches</h2>
      Mushrooms grow in <strong>patches of three</strong>. <br>
      <br>
      <strong>All mushrooms are equally common</strong>, <br>
      and any mushroom is equally likely to grow with any other.<br><br>
      
      <div class="center">
      ${patchListToHTML([[
        {"color": "Green", "texture": "Spotted"}, 
        {"color": "Red", "texture": "Spotted"}, 
        {"color": "Red", "texture": "Striped"}]], true, false)}  
      </div>
      <br>${mushroomModal()}<br>
      Test your knowledge: which is the tastiest?<br>
      <br>`}

function tourGuideJobInstructions() {

    let carla_patch = [[
        {"color": "Green", "texture": "Spotted"},
        {"color": "Red", "texture": "Spotted"},
        {"color": "Red", "texture": "Striped"}]]

    return `
      <h2>Guiding Tourists</h2>
      Visiting tourists pick <strong>one mushroom per patch</strong>.<br>
      Your job is to <strong>help them pick good ones!</strong>
        <div class='center flex-person-wrap'>
        <img src="/static/images/people/Carla.png" width=100px>
        <p>
            Carla is visiting this mushroom patch. <br>
            She'll pick one mushroom from it.
        </p>
      </div>
      <div class="center">
      ${patchListToHTML(carla_patch, false, false)}<br>
      </div>
      Up next: the twist...<br>
`}

function instructOrTeach() {

    //       "Take ${featureRandomization["Spotted"]} ${featureRandomization["Green"]} mushrooms." <br><br>
    //        "${featureRandomization["Green"]} is worth +2." <br><br>
    //       If that feature is not present, they will choose a mushroom <strong>randomly.</strong> <br><br>

    return `
      <h2>Instruct or Teach?</h2>

       <h3>Instructing</h3>
       Instructions tell tourists to take a <strong>specific mushroom</strong>. <br>
       If that mushroom is not present in a patch, they will choose a mushroom randomly.<br>
       <br>
       <span id="instruct-select">"Take&nbsp;&nbsp;${all_texture_select}&nbsp;&nbsp;${all_color_select}&nbsp;&nbsp;mushrooms."</span>
       <br>
       <br>
       
      <h3>Teaching</h3>
       Teaching gives tourists <strong>general information</strong> about kinds of mushrooms. <br>
       They will choose or avoid mushrooms accordingly.<br>
       <br>

       <span id="describe-select">"${all_feature_select}&nbsp;&nbspis worth&nbsp;&nbsp;${all_value_select}."</span> <br><br><br>
                   
       <p style="padding: 10px; border: 3px solid black">
      <strong>When choosing what to say, you should consider both 
      the visible patch and whether the tourist will visit other patches without you. </strong>
       </p>
       
`}

function instructionOrDescribeInstructions() {

    let carla_patch = [[
        {"color": "Green", "texture": "Spotted"},
        {"color": "Green", "texture": "Striped"},
        {"color": "Blue","texture": "Striped"}]]

    return `
      <h2>Instruct or Teach?</h2>
      </div>
              <div class='center flex-person-wrap'>
        <img src="/static/images/people/Carla.png" width=100px>
        <p>
            Carla is visiting <emph>one</emph> mushroom patch. <br>
            She'll pick one mushroom from it.
        </p>
      </div>
      <div class="center">
      ${patchListToHTML(expandPatchToHorizon(carla_patch, 1), false, false)}<br>
    ${instruct_or_describe}<br><br>
     ${placeholder_form}
     ${feature_value_form} 
      ${instruction_select_form}
      </div>
      <br>
        <strong>What would you tell Carla?</strong> <br>
`}

function instructionOrDescribeInstructionsTwo() {

    let carla_patch = [[
        {"color": "Green", "texture": "Spotted"},
        {"color": "Green", "texture": "Striped"},
        {"color": "Blue","texture": "Striped"}]]

    return `
      <h2>Instruct or Teach?</h2>

       <div class='center flex-person-wrap'>
        <img src="/static/images/people/Carla.png" width=100px>
        <p>
            Carla is visiting <strong>two</strong> mushroom patches. <br>
            She'll pick <strong>one mushroom from each</strong>.
        </p>
      </div>
      <div class="center">
      ${patchListToHTML(expandPatchToHorizon(carla_patch, 2), false, false)}<br>
    ${instruct_or_describe}<br><br>
     ${placeholder_form}
     ${feature_value_form} 
     ${instruction_select_form}
      </div>
      <br>
        What would you tell Carla... <strong>if she was visiting a patch without you?</strong> <br>
`}

function touristItineraryInstructions() {

    let steve_patch = [[
        {"color": "Green", "texture": "Solid"},
        {"color": "Blue", "texture": "Spotted"},
        {"color": "Red", "texture": "Striped"}]]

    var evelyn_patch = [[
        {"color": "Blue", "texture": "Spotted"},
        {"color": "Green", "texture": "Solid"},
        {"color": "Green", "texture": "Striped"}]]

    return `
      <h2>Multiple Patches!</h2>
      Tourists visit <strong>one to four patches.</strong><br>
      However, you only accompany them to <strong>one.</strong><br>
      They visit the others without you.<br>
      
      <div class='center flex-person-wrap'>
        <img src="/static/images/people/Evelyn.png" width=100px>
        <p>Evelyn is visiting <emph>one</emph> mushroom patch.<br>
        She'll pick one mushroom from it.</p>
      </div>
      <div class="center">
      ${patchListToHTML(expandPatchToHorizon(evelyn_patch,1))}
      </div>
        <div class='center flex-person-wrap'>
        <img src="/static/images/people/Steve.png" width=100px>
        <p>
            Steve is visiting <emph>four</emph> mushroom patches.<br>
            He'll pick one mushroom from each.
        </p>
      </div>
      <div class="center">
      ${patchListToHTML(expandPatchToHorizon(steve_patch, 4))}
      </div>
      <br>
      <p style="padding: 10px; border: 3px solid black">
      <strong>You should try to help them pick good mushrooms throughout their visit.
      <br></strong>
      </p>
      <br>
      Up next: how to advise tourists...<br>
`}

function studyHallInstructions(repetition) {
    return `
      <h2>Forest of Fungi&trade;<br>Tour Guide Certification Test&trade;</h2>
      <br>
      It's time to take the test!<br>
      You must get all questions correct to proceed. <br>
      <br>
      <strong>If you fail 3 times, the experiment will end <br>
      and you will not recieve the completion bonus.</strong><br>
      <br>
      You have <strong>${3 - repetition}</strong> attempts remaining.<br>
      Click "Previous" to review, or "Next" to take the test.<br><br>
      Good luck!<br><br>
      ${mushroomModal()}
    `}