const resumeInput = document.getElementById("resume");
const fileName = document.getElementById("file-name");

resumeInput.addEventListener("change", function () {

    if (this.files.length > 0) {

        const file = this.files[0];

        fileName.innerHTML = "Selected File: <strong>" + file.name + "</strong>";

    } else {

        fileName.innerHTML = "";

    }

});