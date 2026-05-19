from django.shortcuts import render
# from .decorators import candidate_login_required


# @candidate_login_required
def candidate_dashboard(request):
    return render(request, 'candidate/candidate_dashboard.html')


# @candidate_login_required
# def profile(request):
#     return render(request, 'candidate/profile.html')