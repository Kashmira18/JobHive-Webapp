document.addEventListener('DOMContentLoaded', function () {

    // --- 1. Profile Update Handling ---
    const updateProfileBtn = document.querySelectorAll('.btn-update')[0]; // The first button

    if (updateProfileBtn) {
        updateProfileBtn.addEventListener('click', function (e) {
            e.preventDefault(); // Stop the form from submitting normally

            // Helper to get value by input index in the first form
            // Note: This relies on the specific order of your HTML elements
            const inputs = document.forms[0].querySelectorAll('input, select');

            const profileData = {
                firstName: inputs[0].value,
                lastName: inputs[1].value,
                phone: inputs[2].value,
                email: inputs[3].value,
                profession: inputs[4].value,
                jobRole: inputs[5].value,
                qualification: inputs[6].value,
                experience: inputs[7].value,
                dob: inputs[8].value,
                location: inputs[9].value,
                website: inputs[10].value,

                // Get the content from the "contenteditable" Bio div
                bio: document.querySelector('.editor-content').innerHTML.trim(),

                // Get Toggle States
                settings: {
                    availableForHiring: document.querySelectorAll('.form-check-input')[0].checked,
                    publicProfile: document.querySelectorAll('.form-check-input')[1].checked,
                    hideCV: document.querySelectorAll('.form-check-input')[2].checked
                }
            };

            console.log("--------------- Profile Data ---------------");
            console.log(profileData);
            alert(`Profile Updated for ${profileData.firstName} ${profileData.lastName}! \n(Check console for data object)`);
        });
    }

    // --- 2. Social Network Update Handling ---
    const updateSocialBtn = document.querySelectorAll('.btn-update')[1]; // The second button

    if (updateSocialBtn) {
        updateSocialBtn.addEventListener('click', function (e) {
            e.preventDefault();

            // Select inputs strictly within the second form
            const socialInputs = document.forms[1].querySelectorAll('input');

            const socialData = {
                facebook: socialInputs[0].value,
                twitter: socialInputs[1].value,
                linkedin: socialInputs[2].value,
                pinterest: socialInputs[3].value,
                dribbble: socialInputs[4].value,
                behance: socialInputs[5].value
            };

            console.log("--------------- Social Data ---------------");
            console.log(socialData);
            alert("Social Networks Updated Successfully!");
        });
    }

    // --- 3. Optional: Rich Text Toolbar Logic ---
    // Since your HTML code snippet didn't include the toolbar buttons, 
    // this logic is here in case you add them back later.
    const editorButtons = document.querySelectorAll('.editor-btn');
    if (editorButtons.length > 0) {
        editorButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const command = btn.getAttribute('data-command');
                if (command) {
                    document.execCommand(command, false, null);
                }
            });
        });
    }
});
