const jobs = [
    {
        title: "Looking for Delivery Driver",
        company: "jobee.io · Bangladesh",
        salary: "Rs60000–Rs70000 / Month",
        date: "28 Nov, 2025",
        summary: "Experience: 3 Years\nExpected Salary: 0",
        status: "HIRED"
    },
    {
        title: "Creative UI/UX Designer",
        company: "New Desire Solution · Mirpur",
        salary: "Negotiable",
        date: "16 Nov, 2025",
        summary: "Experience: 3 Years\nExpected Salary: 50000",
        status: "APPLIED"
    }
];

const body = document.getElementById("jobBody");
const info = document.getElementById("jobInfo");

function renderJobs() {
    body.innerHTML = "";

    jobs.forEach(job => {
        body.innerHTML += `
      <div class="job-row">
        <div class="job-info">
          <div class="job-logo">${job.title[0]}</div>
          <div>
            <div class="job-title">${job.title}</div>
            <div class="job-meta">${job.company}</div>
            <div class="job-meta">${job.salary}</div>
          </div>
        </div>
        <div>${job.date}</div>
        <div class="summary">${job.summary.replace("\n", "<br>")}</div>
        <div>
          <span class="badge ${job.status === "HIRED" ? "badge-hired" : "badge-applied"} px-3 py-2">
            ${job.status}
          </span>
        </div>
      </div>
    `;
    });

    info.textContent = `Showing 1–${jobs.length} of ${jobs.length} jobs`;
}

renderJobs();


