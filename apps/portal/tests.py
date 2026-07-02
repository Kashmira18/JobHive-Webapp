from django.template.loader import get_template
from django.test import TestCase
from django.urls import reverse
from accounts.models import CompanyProfile, CustomUser
from job.models import JobPost


class HomeTemplateTests(TestCase):
    def test_home_template_renders_without_reverse_errors(self):
        template = get_template("portal/home.html")
        html = template.render(
            {
                "total_jobs": 0,
                "published_jobs": [],
                "recent_jobs": [],
                "trending_jobs": [],
            }
        )

        self.assertIn("JobHive Statistics", html)
        self.assertIn("Choose Your Dream Job", html)


class HomePublishedJobsTests(TestCase):
    def test_home_view_passes_all_published_jobs_to_template(self):
        user = CustomUser.objects.create_user(username="company2", email="company2@example.com", password="secret")
        company = CompanyProfile.objects.create(user=user, trade_name="Globex")
        JobPost.objects.create(
            company=company,
            title="Backend Engineer",
            category="Engineering",
            experience_level="Mid",
            job_type="Full-Time",
            location="Islamabad",
            work_mode="Remote",
            deadline="2030-12-31",
            description="Build backend services.",
            qualifications="Python experience",
            minimum_education="Bachelor",
            years_of_experience="3+",
            skills="Python,Django",
            visibility="public",
            status="PUBLISHED",
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend Engineer")


class JobListingFilterTests(TestCase):
    def setUp(self):
        user = CustomUser.objects.create_user(username="company", email="company@example.com", password="secret")
        company = CompanyProfile.objects.create(user=user, trade_name="Acme Labs")
        JobPost.objects.create(
            company=company,
            title="Django Developer",
            category="Engineering",
            experience_level="Mid",
            job_type="Full-Time",
            location="Remote",
            work_mode="Remote",
            deadline="2030-12-31",
            description="Build web apps with Django.",
            qualifications="Python experience",
            minimum_education="Bachelor",
            years_of_experience="3+",
            skills="Python,Django",
            visibility="public",
            status="PUBLISHED",
        )
        JobPost.objects.create(
            company=company,
            title="UI Designer",
            category="Design",
            experience_level="Junior",
            job_type="Part-Time",
            location="Lahore",
            work_mode="On-site",
            deadline="2030-12-31",
            description="Design beautiful interfaces.",
            qualifications="Figma experience",
            minimum_education="Bachelor",
            years_of_experience="1+",
            skills="Figma,UI",
            visibility="public",
            status="PUBLISHED",
        )

    def test_job_listing_filters_by_keyword_location_and_category(self):
        response = self.client.get(
            reverse("job_list"),
            {"keyword": "django", "location": "remote", "category": "engineering"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Developer")
        self.assertNotContains(response, "UI Designer")
