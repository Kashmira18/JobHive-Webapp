from django.shortcuts import render

# Create your views here.

# from .decorators import candidate_login_required


# @candidate_login_required
def dashboard(request):
    return render(request, 'company/company_dashboard.html')

def base(request):
    return render(request, 'company/company_base.html')


