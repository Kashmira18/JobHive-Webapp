from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .models import JobPost

def job_list(request):
    return render(request, "job/job_list.html")

def job_detail(request, pk):
    try:
        job = JobPost.objects.get(id=pk)
        if job.status != "PUBLISHED" or job.visibility != "public":
            messages.warning(request, "This job is no longer available.")
            return redirect('job_list')
    except ObjectDoesNotExist:
        messages.error(request, "This job does not exist.")
        return redirect('job_list')

    return render(request, "portal/job_details.html", {"job": job, "pk": pk})
