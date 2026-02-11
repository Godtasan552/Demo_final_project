from django.contrib import admin
from .models import UserProfile, Project, EvaluationForm, RequestForm, Submission

# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'role', 'department', 'phone']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'user__first_name',
                     'user__last_name', 'student_id']
    ordering = ['student_id', 'user__username']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title_th', 'status', 'advisor', 'created_at']
    list_filter = ['status', 'advisor', 'created_at']
    search_fields = ['title_th', 'title_en', 'description']
    filter_horizontal = ['students']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(EvaluationForm)
class EvaluationFormAdmin(admin.ModelAdmin):
    list_display = ['project', 'form_type', 'evaluator',
                    'score', 'is_approved', 'submitted_at']
    list_filter = ['form_type', 'is_approved', 'submitted_at']
    search_fields = ['project__title_th', 'evaluator__username', 'comments']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']


@admin.register(RequestForm)
class RequestFormAdmin(admin.ModelAdmin):
    list_display = ['project', 'form_type',
                    'submitted_by', 'status', 'submitted_at']
    list_filter = ['form_type', 'status', 'submitted_at']
    search_fields = ['project__title_th',
                     'submitted_by__username', 'request_details']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'project',
                    'submission_type', 'submitted_by', 'submitted_at']
    list_filter = ['submission_type', 'submitted_at']
    search_fields = ['title', 'project__title_th', 'description']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']
