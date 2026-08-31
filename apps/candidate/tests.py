from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import CustomUser


class CandidateDashboardAccessAndContextTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.candidate = CustomUser.objects.create_user(
            username='candidateuser',
            email='candidate@example.com',
            password='Password123!',
            role='CANDIDATE',
            is_approved=True,
        )

    def test_candidate_dashboard_renders_required_context_for_new_candidate(self):
        self.client.force_login(self.candidate)

        response = self.client.get(reverse('candidate:candidate_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('total_applied', response.context)
        self.assertIn('saved_jobs', response.context)
        self.assertIn('status_breakdown', response.context)
        self.assertIn('recent_notifications', response.context)
        self.assertIn('completion_percentage', response.context)
        self.assertEqual(response.context['total_applied'], 0)
        self.assertEqual(response.context['saved_jobs'], 0)
        self.assertEqual(response.context['status_breakdown']['APPLIED'], 0)
        self.assertEqual(response.context['completion_percentage'], 0)

    def test_company_user_is_redirected_from_candidate_dashboard(self):
        company = CustomUser.objects.create_user(
            username='companyuser',
            email='company@example.com',
            password='Password123!',
            role='COMPANY',
            is_approved=True,
        )
        self.client.force_login(company)

        response = self.client.get(reverse('candidate:candidate_dashboard'))

        self.assertIn(response.status_code, (302, 403))

    def test_profile_setup_template_uses_valid_choice_values(self):
        self.client.force_login(self.candidate)

        response = self.client.get(reverse('candidate:candidate_edit_profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="full_time"')
        self.assertContains(response, 'value="part_time"')
        self.assertContains(response, 'value="remote"')

    def test_dashboard_and_profile_views_expose_user_avatar_url_with_default_fallback(self):
        self.client.force_login(self.candidate)

        dashboard_response = self.client.get(reverse('candidate:candidate_dashboard'))
        profile_response = self.client.get(reverse('candidate:candidate_edit_profile'))

        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(profile_response.status_code, 200)
        self.assertIn('profile_photo_url', dashboard_response.context)
        self.assertIn('profile_photo_url', profile_response.context)
        self.assertIn('default-avatar', dashboard_response.context['profile_photo_url'])
        self.assertIn('default-avatar', profile_response.context['profile_photo_url'])
