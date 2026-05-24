const bookmarkJobs = [
    {
        title: "Front End Devloper",
        location: "Mirpur, Bangladesh",
        salary: "Negotiable",
        deadline: "28 Feb, 2026",
        company: "City Life Travel",
        logo: "https://via.placeholder.com/48/1a2a40/ffffff?text=C" // Replace with actual logo URL
    },
    {
        title: "Ready to hire a Lead Designer",
        location: "Mirpur, Bangladesh",
        salary: "Negotiable",
        deadline: "28 Feb, 2026",
        company: "New Desire Solution",
        logo: "https://via.placeholder.com/48/0b0b2a/ffffff?text=N" // Replace with actual logo URL
    },
    {
        title: "We are Hiring Legal Advisor",
        location: "Mirpur, Bangladesh",
        salary: "R$20000 - R$30000 /Per Month",
        deadline: "28 Feb, 2026",
        company: "Best Solution",
        logo: "https://via.placeholder.com/48/00d4ff/ffffff?text=B" // Replace with actual logo URL
    }
];

const tableBody = document.getElementById('bookmark-table-body');

// Map through data and create rows
bookmarkJobs.forEach(job => {
    const row = `
        <tr>
            <td>
                <div class="d-flex align-items-center">
                    <img src="${job.logo}" class="job-logo me-3" alt="company logo">
                    <div>
                        <div class="job-title">${job.title}</div>
                        <div class="job-meta">
                            <div><i class="fa-solid fa-location-dot"></i> ${job.location}</div>
                            <div><i class="fa-regular fa-compass"></i> Salary: ${job.salary}</div>
                        </div>
                    </div>
                </div>
            </td>
            <td><span class="deadline-text">${job.deadline}</span></td>
            <td><span class="company-text">${job.company}</span></td>
            <td class="text-center">
                <a href="#" class="apply-now">Apply Now</a>
            </td>
        </tr>
    `;
    tableBody.innerHTML += row;
});
