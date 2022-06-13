function template(strings, ...keys) {
    return (function(...values) {
        let dict = values[values.length - 1] || {};
        let result = [strings[0]];
        keys.forEach(function(key, i) {
            let value = Number.isInteger(key) ? values[key] : dict[key];
            result.push(value, strings[i + 1]);
        });
        return result.join('');
    });
}

function mushroomListToHTML(mushroomList, showName=false, shuffleMushrooms=true) {

    var patchString = `<div class="center flex-mushroom-patch">`

    if (shuffleMushrooms) {mushroomList = _.shuffle(mushroomList)}

    // loop over mushrooms
    // Carlos: replace with map? don't need to iterate over list

    for (var i = 0; i < mushroomList.length; i++) {
        patchString += mushroomToHTML(mushroomList[i], showName)
    }

    patchString += `</div>`

    return patchString
}

function mushroomToHTML(canonicalAction, showName) {

    let mushroomValueClosure = template`<span class='tripartite'>
        <img src="/static/images/mushrooms/${'color'}-${'texture'}.png" class='tripartite' title="${'color'} ${'texture'}">
        <figcaption class="fontsize12">Value: ${'value'}</figcaption></span>`

    let mushroomFeatureClosure = template`<span class='tripartite'>
        <img src="/static/images/mushrooms/${'color'}-${'texture'}.png" class='tripartite' title="${'color'} ${'texture'}">
        <figcaption class="fontsize12">${'texture'} ${'color'}</figcaption></span>`

    if(canonicalAction["color"] === "unknown"){
        return mushroomFeatureClosure({"color": "unknown", "texture": "", "value": "?"})
    }

    let mushroomClosure = showName ? mushroomFeatureClosure : mushroomValueClosure;

    let mushroomDisplay = {
        "color": featureRandomization[canonicalAction["color"]],
        "texture": featureRandomization[canonicalAction["texture"]],
        "value": canonicalFeatureValues[canonicalAction["color"]] + canonicalFeatureValues[canonicalAction["texture"]]
    }

    return mushroomClosure(mushroomDisplay)

}

function patchListToHTML(patchList, showName=false, shuffleMushrooms=false) {

    let patchesString = `<div class='center flex-mushroom-wrap'>`

    for (let i = 0; i < patchList.length; i++) {
        patchesString += mushroomListToHTML(patchList[i], showName, shuffleMushrooms);
    }

    patchesString += '</div>'
    return patchesString
}

/////////// GENERATING MUSHROOM CHEAT SHEET //////////////////

function cheatsheetFeatureToHTML(canonicalFeature, showValue=true) {

    let featureClosureWithValue = template`<img src="/static/images/mushrooms/features/${'feature'}.png" 
                                    width=80><figcaption><p class="fontsize12">${'feature'}: ${'value'}</p></figcaption>`

    let featureClosureNoValue = template`<img src="/static/images/mushrooms/features/${'feature'}.png" title="${'feature'}"
                                    width=60>`

    let featureClosure = showValue ? featureClosureWithValue : featureClosureNoValue;

    let feature = featureRandomization[canonicalFeature]

    return featureClosure({'feature':feature, 'value': canonicalFeatureValues[canonicalFeature]})

}

function cheatsheetMushroomToHTML(canonicalAction) {

    let mushroomClosure = template`<div class="col-sm-3"><span>
        <img src="/static/images/mushrooms/${'color'}-${'texture'}.png" class='tripartite' title="${'tooltip'}">
        <figcaption class="fontsize12">Value: ${'value'}</figcaption></span></div>`

    let mushroomDisplay = {
        "color": featureRandomization[canonicalAction["color"]],
        "texture": featureRandomization[canonicalAction["texture"]],
        "value": canonicalFeatureValues[canonicalAction["color"]] + canonicalFeatureValues[canonicalAction["texture"]]
    }

    return mushroomClosure(mushroomDisplay)

}

function generateMushroomCheatSheet() {

    let cheatSheetHTML = '<div class="row">\n<div class="col-sm-3"></div>'
    cheatSheetHTML += '<div class="col-sm-3"><span>'
    cheatSheetHTML += cheatsheetFeatureToHTML("Green") + '</span></div>'
    cheatSheetHTML += '<div class="col-sm-3"><span>'
    cheatSheetHTML += cheatsheetFeatureToHTML("Red") + '</span></div>'
    cheatSheetHTML += '<div class="col-sm-3"><span>'
    cheatSheetHTML += cheatsheetFeatureToHTML("Blue") + '</span></div>'

    cheatSheetHTML += "</div><div class=\"row\">"
    cheatSheetHTML += '<div class="col-sm-3"><span>'
    cheatSheetHTML += cheatsheetFeatureToHTML("Spotted")  + '</span></div>'

    cheatSheetHTML += cheatsheetMushroomToHTML({"color": "Green", "texture":"Spotted"})
    cheatSheetHTML += cheatsheetMushroomToHTML({"color": "Red", "texture":"Spotted"})
    cheatSheetHTML += cheatsheetMushroomToHTML({"color": "Blue", "texture":"Spotted"})

    cheatSheetHTML += "</div><div class=\"row\">"
    cheatSheetHTML += '<div class="col-sm-3"><span>'
    cheatSheetHTML += cheatsheetFeatureToHTML("Solid") + '</span></div>'

    cheatSheetHTML += cheatsheetMushroomToHTML({"color": "Green", "texture":"Solid"})
    cheatSheetHTML += cheatsheetMushroomToHTML({"color": "Red", "texture": "Solid"})
    cheatSheetHTML += cheatsheetMushroomToHTML({"color": "Blue", "texture":"Solid"})

    cheatSheetHTML += "</div><div class=\"row\">"
    cheatSheetHTML += '<div class="col-sm-3"><span>'

    cheatSheetHTML += cheatsheetFeatureToHTML("Striped") + '</span></div>'
    cheatSheetHTML += cheatsheetMushroomToHTML({"color": "Green", "texture":"Striped"})
    cheatSheetHTML += cheatsheetMushroomToHTML({"color": "Red", "texture":"Striped"})
    cheatSheetHTML += cheatsheetMushroomToHTML({"color": "Blue", "texture":"Striped"})
    cheatSheetHTML += "</div>"

    return cheatSheetHTML
}

function expandPatchToHorizon(action_context, horizon) {

    if (horizon === "ambiguous"){ return action_context }

    var unknown_patch = [{"color": "unknown", "texture": "unknown"}, {"color": "unknown", "texture": "unknown"}, {"color": "unknown", "texture": "unknown"}]

    while (action_context.length < horizon) {
        action_context.push(unknown_patch)
    }
    return action_context

}

function mushroomModal() {
    return `<button type="button" class="btn jspsych-btn" data-toggle="modal" data-target="#exampleModalCenter"> 
      View Mushroom Info</button> 
      <div class="modal fade" id="exampleModalCenter" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">  
      <div class="modal-dialog modal-dialog-centered" role="document">  
      <div class="modal-content">  
      <div class="modal-header">  
      <h5 class="modal-title" id="exampleModalLongTitle">Mushroom Info Sheet</h5>  
      <button type="button" class="close" data-dismiss="modal" aria-label="Close">  
      <span aria-hidden="true">&times;</span> 
      </button>  
      </div> 
      <div class="modal-body grid-mushroom-modal">  
      <div class="container-fluid"> 
      ${generateMushroomCheatSheet()}
      </div>  
      </div> 
      <div class="modal-footer">  
      <button type="button" class="btn btn-primary" data-dismiss="modal">Close</button>  
      </div> 
      </div> 
      </div> 
      </div>&nbsp;`}
