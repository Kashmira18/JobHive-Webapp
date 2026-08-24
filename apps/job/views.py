from django.shortcuts import render

# Create your views here.

def job_list(request):
    
    return render(request, "job/job_list.html")

def job_detail(request, pk):
    return render(request, "portal/job_details.html", {"pk": pk})
