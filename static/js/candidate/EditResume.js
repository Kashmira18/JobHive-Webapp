
function removeItem(element) {
    // Removes the parent container of the clicked remove link
    if (confirm('Are you sure you want to remove this section?')) {
        element.parentElement.remove();
    }
}

function addEducation() {
    const container = document.getElementById('education-container');
    // Template for new education item
    const html = `
            <div class="education-item fade-in-animation">
                <p class="text-muted mb-2">Academic Information:</p>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Education Level<span class="required-star">*</span></label>
                        <input type="text" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">My Major<span class="required-star">*</span></label>
                        <input type="text" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Institute/University<span class="required-star">*</span></label>
                        <input type="text" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Result/GPA<span class="required-star">*</span></label>
                        <input type="text" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Starting Period<span class="required-star">*</span></label>
                        <input type="date" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Ending Period<span class="required-star">*</span></label>
                        <input type="date" class="form-control">
                    </div>
                </div>
                <a class="remove-link" onclick="removeItem(this)">Remove Education Area</a>
                <div class="section-separator"></div>
            </div>
        `;
    container.insertAdjacentHTML('beforeend', html);
}

function addExperience() {
    const container = document.getElementById('experience-container');
    // Template for new experience item
    const html = `
            <div class="experience-item fade-in-animation">
                <p class="text-muted mb-2">Add Your Experiences</p>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Company Name<span class="required-star">*</span></label>
                        <input type="text" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Designation<span class="required-star">*</span></label>
                        <input type="text" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Starting Period<span class="required-star">*</span></label>
                        <input type="date" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Ending Period<span class="required-star">*</span></label>
                        <input type="date" class="form-control">
                    </div>
                    <div class="col-12 mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox">
                            <label class="form-check-label">Continuing Working Here</label>
                        </div>
                    </div>
                    <div class="col-12 mb-3">
                        <label class="form-label">Responsibility</label>
                        <textarea class="form-control" rows="3"></textarea>
                    </div>
                </div>
                <a class="remove-link" onclick="removeItem(this)">Remove Experience Area</a>
                <div class="section-separator"></div>
            </div>
        `;
    container.insertAdjacentHTML('beforeend', html);
}

