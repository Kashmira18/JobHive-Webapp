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
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin_layout/", views.admin_layout, name="layout"),
    path("company_type/", views.company_type, name="company_type"),
    path("company_type/create/", views.company_type_create, name="company_type_create"),
    path("company_type/delete/<int:type_id>/", views.company_type_delete, name="company_type_delete"),
    path("company_type/toggle/<int:type_id>/", views.company_type_toggle, name="company_type_toggle"),

    path("admin_company", views.admin_company, name="admin_company"),
    path("admin_jobs", views.admin_jobs, name="admin_jobs"),

    path("job_type", views.job_type, name="job_type"),
    path("job_type/create/", views.job_type_create, name="job_type_create"),
    path("job_type/delete/<int:type_id>/", views.job_type_delete, name="job_type_delete"),
    path("job_type/toggle/<int:type_id>/", views.job_type_toggle, name="job_type_toggle"),

    path("admin_users", views.admin_users, name="admin_users"),
    path("admin_users/create/", views.admin_users_create, name="admin_users_create"),
    path("admin_users/delete/<int:user_id>/", views.admin_users_delete, name="admin_users_delete"),

    path("job_categories", views.job_categories, name="job_categories"),
    path("job_categories/create/", views.job_categories_create, name="job_categories_create"),
    path("job_categories/delete/<int:cat_id>/", views.job_categories_delete, name="job_categories_delete"),
    path("job_categories/toggle/<int:cat_id>/", views.job_categories_toggle, name="job_categories_toggle"),

    path("candidate_list", views.candidate_list, name="candidate_list"),
    path("candidate_list/create/", views.candidate_list_create, name="candidate_list_create"),
    path("candidate_list/delete/<int:user_id>/", views.candidate_list_delete, name="candidate_list_delete"),

    path('companies/', views.admin_company_list, name='admin_company_list'),
    path('company/<int:user_id>/approve', views.approve_company, name='approve_company'),
    
    path('company/<int:user_id>/reject', views.reject_company, name='reject_company'),
    
    path("company/<int:user_id>/details/",  views.view_company_details, name="view_company_details"),
    path("company/<int:user_id>/rollback/", views.rollback_company,     name="rollback_company"),
    # path("company/<int:user_id>/delete/",   views.delete_company,       name="delete_company"),
    # path("company/<int:user_id>/edit/",     views.edit_company,         name="edit_company"),
    # path("company/<int:user_id>/update/",   views.update_company,       name="update_company"),
    #_________billing____________
    # path("billing/", views.admin_billing, name="billing"),
    path("payments/", views.admin_payments, name="admin_payments"),
    path("payments/<int:log_id>/approve/", views.approve_payment, name="approve_payment"),
    path("payments/<int:log_id>/reject/", views.reject_payment, name="reject_payment"),
    path("plans/manage/", views.manage_plans, name="manage_plans"),
    path("plans/<int:plan_id>/edit/", views.edit_plan, name="edit_plan"),
    path("plans/<int:plan_id>/delete/", views.delete_plan, name="delete_plan"),
    path("plans/<int:plan_id>/toggle-status/", views.toggle_plan_status, name="toggle_plan_status"),
]