from django.urls import path
from . import views

app_name = "custom_admin"

urlpatterns = [
    # ── Auth ──────────────────────────────────────────
    path("login/", views.admin_login, name="login"),
    path("logout/", views.admin_logout, name="logout"),
    path("forgot-password/",views.admin_forgot_password, name="forgot_password"),
    path("reset-password/<uidb64>/<token>/",views.admin_reset_password, name="reset_password",
    ),

    # ── Dashboard ─────────────────────────────────────
    path("dashboard/", views.admin_dashboard, name="dashboard"),

    # ─────────────────────────────────────────────────
    # Aap yahan apne baqi views add karte jayen:
    # path("users/",        views.user_list,             name="user_list"),
    # path("jobs/",         views.job_list,              name="job_list"),
    # ─────────────────────────────────────────────────
]