document.addEventListener('DOMContentLoaded', function () {

    // --- 1. Sidebar Navigation Active State ---
    const navLinks = document.querySelectorAll('.sidebar .nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            // Optional: Prevent default if you don't have real pages yet
            // e.preventDefault(); 

            // Remove 'active' class and specific styling from all links
            navLinks.forEach(nav => {
                nav.classList.remove('active', 'text-primary', 'fw-bold');
                nav.classList.add('text-dark'); // Reset to default color if needed
            });

            // Add active styling to the clicked link
            this.classList.remove('text-dark');
            this.classList.add('active', 'text-primary', 'fw-bold');
        });
    });

    // --- 2. Statistics Counter Animation ---
    // This makes the numbers (20, 8, 5, 39) count up smoothly on load
    const stats = document.querySelectorAll('.stat-number');

    stats.forEach(stat => {
        const target = +stat.innerText; // Get the number from HTML
        const speed = 200; // The lower the slower
        const increment = target / speed;

        let current = 0;

        const updateCount = () => {
            if (current < target) {
                current += Math.ceil(target / 40); // Increment step
                if (current > target) current = target;
                stat.innerText = current;
                setTimeout(updateCount, 40);
            } else {
                stat.innerText = target;
            }
        };

        updateCount();
    });

    // --- 3. Heart / Bookmark Toggle Logic ---
    // Finds all heart icons inside featured cards or job lists
    const hearts = document.querySelectorAll('.fa-heart');

    hearts.forEach(heart => {
        heart.style.cursor = 'pointer'; // Make it look clickable
        heart.addEventListener('click', function (e) {
            e.preventDefault(); // Stop link navigation if inside an anchor tag

            // Toggle between Solid (fas) and Outline (far) classes
            if (this.classList.contains('far')) {
                this.classList.remove('far', 'text-muted');
                this.classList.add('fas', 'text-danger'); // Make it solid red
            } else {
                this.classList.remove('fas', 'text-danger');
                this.classList.add('far', 'text-muted'); // Make it outline grey
            }
        });
    });

    // --- 4. Table "Status" Button Interaction ---
    const statusButtons = document.querySelectorAll('.status-btn');

    statusButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            // Find the parent row (tr) of the clicked button
            const row = this.closest('tr');

            // Extract data from that specific row
            const jobTitle = row.querySelector('.job-title').innerText;
            const companyName = row.querySelector('.company-name').innerText.trim();
            const statusText = this.innerText;

            alert(`Job Details:\n\nRole: ${jobTitle}\nCompany: ${companyName}\nCurrent Status: ${statusText}`);
        });
    });

    // --- 5. "Apply Now" Button Logic ---
    const applyLinks = document.querySelectorAll('.apply-link');

    applyLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const card = this.closest('.featured-card');
            const title = card.querySelector('.featured-title').innerText;

            // Simulate sending data
            const confirmApply = confirm(`Do you want to apply for "${title}"?`);

            if (confirmApply) {
                this.innerHTML = 'Applied <i class="fas fa-check"></i>';
                this.classList.add('text-success');
                this.classList.remove('text-danger');
                this.style.pointerEvents = 'none'; // Disable clicking again
            }
        });
    });

});
