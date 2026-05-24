function addEducation() {
    const container = document.getElementById('education-list');
    const newEntry = document.createElement('div');
    newEntry.className = 'education-item border-bottom pb-3 mb-3 mt-3';
    newEntry.innerHTML = `
        <div class="row g-3">
            <div class="col-md-6">
                <label class="form-label">Education Level*</label>
                <input type="text" class="form-control">
            </div>
            <div class="col-md-6">
                <label class="form-label">My Major*</label>
                <input type="text" class="form-control">
            </div>
        </div>
        <button class="btn btn-link text-danger p-0 mt-2" onclick="this.parentElement.remove()">Remove Education Area</button>
    `;
    container.appendChild(newEntry);
}
