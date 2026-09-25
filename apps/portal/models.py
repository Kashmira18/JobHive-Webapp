from django.db import models

class BlogCategory(models.TextChoices):
    RESUME_TIPS = 'resume-tips', 'Resume Tips'
    INTERVIEW_PREP = 'interview-prep', 'Interview Prep'
    HIRING_GUIDES = 'hiring-guides', 'Hiring Guides'

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=BlogCategory.choices)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    excerpt = models.TextField()
    content = models.TextField(blank=True)
    read_time = models.IntegerField(help_text="Read time in minutes")
    image_url = models.CharField(max_length=255, default='images/blog-img1.webp')
    def __str__(self):
        return self.title
