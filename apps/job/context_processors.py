from .models import JobCategory, JobPost

def global_job_categories(request):
    """
    Makes the active job categories available globally in all templates.
    """
    categories = list(JobCategory.objects.filter(is_active=True).order_by('name'))
    for cat in categories:
        cat.job_count = JobPost.objects.filter(category=cat.name, status="PUBLISHED").count()
        
    return {
        'global_job_categories': categories
    }
