from django.urls import path
from . import views

app_name = 'final_pro'

urlpatterns = [
    path('', views.home, name='home'),

    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/create/', views.project_create, name='project_create'),

    # Evaluation URLs
    path('evaluations/', views.evaluation_list, name='evaluation_list'),
    path('projects/<int:project_pk>/evaluate/',
         views.evaluation_create, name='evaluation_create'),

    # Request URLs
    path('requests/', views.request_list, name='request_list'),
    path('projects/<int:project_pk>/request/',
         views.request_create, name='request_create'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Export documents
    path('projects/<int:pk>/export/<str:form_type>/',
         views.export_project_docx, name='export_project_docx'),

    # Success page
    path('success/', views.submission_success, name='submission_success'),
]
