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
    path("admin_layout/", views.admin_layout, name="layout"),
    path("company_type/", views.company_type, name="company_type"),
    path('companies/', views.admin_company_list, name='admin_company_list'),
    path('company/approve/<int:user_id>/', views.approve_company, name='approve_company'),
    path('company/reject/<int:user_id>/', views.reject_company, name='reject_company'),

        path("company/<int:user_id>/details/",  views.view_company_details, name="view_company_details"),
    # path("company/<int:user_id>/approve/",  views.approve_company,      name="approve_company"),
    # path("company/<int:user_id>/reject/",   views.reject_company,       name="reject_company"),
    path("company/<int:user_id>/rollback/", views.rollback_company,     name="rollback_company"),
    path("company/<int:user_id>/delete/",   views.delete_company,       name="delete_company"),
    path("company/<int:user_id>/edit/",     views.edit_company,         name="edit_company"),
    # path("company/<int:user_id>/update/",   views.update_company,       name="update_company")
]