from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Project, EvaluationForm, RequestForm
from .forms import ProjectForm, EvaluationFormSubmission, RequestFormSubmission

# Create your views here.


def home(request):
    """Home page view"""
    projects = Project.objects.all()[:6]  # Latest 6 projects
    context = {
        'projects': projects,
        'total_projects': Project.objects.count(),
        'total_evaluations': EvaluationForm.objects.count(),
        'total_requests': RequestForm.objects.count(),
    }
    return render(request, 'home.html', context)


def project_list(request):
    """List all projects"""
    projects = Project.objects.all()
    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status=status_filter)

    context = {
        'projects': projects,
        'status_choices': Project.STATUS_CHOICES,
    }
    return render(request, 'project_list.html', context)


def project_detail(request, pk):
    """Project detail view"""
    project = get_object_or_404(Project, pk=pk)
    evaluations = project.evaluations.all()
    requests = project.requests.all()
    submissions = project.submissions.all()

    context = {
        'project': project,
        'evaluations': evaluations,
        'requests': requests,
        'submissions': submissions,
    }
    return render(request, 'project_detail.html', context)


@login_required
def project_create(request):
    """Create new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'สร้างโครงงานสำเร็จ!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()

    return render(request, 'project_form.html', {'form': form, 'title': 'สร้างโครงงานใหม่'})


def evaluation_list(request):
    """List all evaluation forms"""
    evaluations = EvaluationForm.objects.all()
    form_type = request.GET.get('form_type')
    if form_type:
        evaluations = evaluations.filter(form_type=form_type)

    context = {
        'evaluations': evaluations,
        'form_types': EvaluationForm.FORM_TYPES,
    }
    return render(request, 'evaluation_list.html', context)


@login_required
def evaluation_create(request, project_pk):
    """Create evaluation form for a project"""
    project = get_object_or_404(Project, pk=project_pk)

    if request.method == 'POST':
        form = EvaluationFormSubmission(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.project = project
            evaluation.evaluator = request.user
            evaluation.save()
            messages.success(request, 'ส่งแบบประเมินสำเร็จ!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = EvaluationFormSubmission()

    context = {
        'form': form,
        'project': project,
        'title': 'ส่งแบบประเมิน'
    }
    return render(request, 'evaluation_form.html', context)


def request_list(request):
    """List all request forms"""
    requests = RequestForm.objects.all()
    form_type = request.GET.get('form_type')
    status = request.GET.get('status')

    if form_type:
        requests = requests.filter(form_type=form_type)
    if status:
        requests = requests.filter(status=status)

    context = {
        'requests': requests,
        'form_types': RequestForm.FORM_TYPES,
        'status_choices': RequestForm.STATUS_CHOICES,
    }
    return render(request, 'request_list.html', context)


@login_required
def request_create(request, project_pk):
    """Create request form for a project"""
    project = get_object_or_404(Project, pk=project_pk)

    if request.method == 'POST':
        form = RequestFormSubmission(request.POST)
        if form.is_valid():
            request_form = form.save(commit=False)
            request_form.project = project
            request_form.submitted_by = request.user
            request_form.save()
            messages.success(request, 'ส่งคำขอสำเร็จ!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = RequestFormSubmission()

    context = {
        'form': form,
        'project': project,
        'title': 'ส่งแบบคำขอ'
    }
    return render(request, 'request_form.html', context)


def login_view(request):
    """Custom login view with split/sliding interface logic"""
    if request.user.is_authenticated:
        return redirect('final_pro:home')

    target_panel = request.POST.get('target_panel', 'student')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"ยินดีต้อนรับคุณ {user.username}!")

            # Use redirect to admin index if staff
            if user.is_staff:
                return redirect('admin:index')
            return redirect('final_pro:home')
        # If form is invalid, we fall through and specific errors stay in this 'form' instance
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form, 'target_panel': target_panel})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, "ออกจากระบบเรียบร้อยแล้ว")
    return redirect('final_pro:home')


def submission_success(request):
    """Success page after submission"""
    return render(request, 'submission_success.html')
