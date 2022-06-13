function instructButton(){

    console.log("clicked instruct - index.html")

    document.getElementById('placeholder').style.display = "none";

    document.getElementById('instruct-button').removeAttribute("required")
    document.getElementById('describe-button').removeAttribute("required")

    document.getElementById('describe-select').style.display = "none";
    document.getElementById('feature-select').removeAttribute("required")
    document.getElementById('feature-select').selectedIndex = 0
    document.getElementById('value-select').removeAttribute("required")
    document.getElementById('value-select').selectedIndex = 0

    document.getElementById('instruct-select').style.display = "block";
    document.getElementById('color-select').setAttribute("required", "")
    document.getElementById('texture-select').setAttribute("required", "")
}
function describeButton() {

    console.log("clicked describe - index.html")
    document.getElementById('placeholder').style.display = "none";

    document.getElementById('instruct-button').removeAttribute("required")
    document.getElementById('describe-button').removeAttribute("required")

    document.getElementById('describe-select').style.display = "block";
    document.getElementById('feature-select').setAttribute("required", "")
    document.getElementById('value-select').setAttribute("required", "")

    document.getElementById('instruct-select').style.display = "none";
    document.getElementById('color-select').removeAttribute("required")
    document.getElementById('color-select').selectedIndex = 0
    document.getElementById('texture-select').removeAttribute("required")
    document.getElementById('texture-select').selectedIndex = 0

}