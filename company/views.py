from django.shortcuts import render

# Create your views here.

# from .decorators import candidate_login_required


# @candidate_login_required
def dashboard(request):
    return render(request, 'company/company_dashboard.html')


# @candidate_login_required
# def profile(request):
#     return render(request, 'candidate/profile.html')