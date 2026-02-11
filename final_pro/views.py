from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Project, EvaluationForm, RequestForm, UserProfile
from .forms import ProjectForm, EvaluationFormSubmission, RequestFormSubmission, StudentRegistrationForm
from .document_generator import generate_project_document
from django.http import HttpResponse
import os

# Create your views here.


def home(request):
    """Home page view with role-based visibility"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            projects = Project.objects.all()[:6]
        elif request.user.is_staff:
            projects = Project.objects.filter(
                Q(advisor=request.user) | Q(co_advisor=request.user))[:6]
        else:
            projects = Project.objects.filter(students=request.user)[:6]
    else:
        projects = Project.objects.none()

    context = {
        'projects': projects,
        'total_projects': Project.objects.count(),
        'total_evaluations': EvaluationForm.objects.count(),
        'total_requests': RequestForm.objects.count(),
    }
    return render(request, 'home.html', context)


@login_required
def project_list(request):
    """List projects based on user role and permissions"""
    if request.user.is_superuser:
        projects = Project.objects.all()
    elif request.user.is_staff:
        # Advisors can see projects where they are advisor or co-advisor
        projects = Project.objects.filter(
            Q(advisor=request.user) | Q(co_advisor=request.user))
    else:
        # Students can only see their own projects
        projects = Project.objects.filter(students=request.user)

    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status=status_filter)

    context = {
        'projects': projects,
        'status_choices': Project.STATUS_CHOICES,
    }
    return render(request, 'project_list.html', context)


@login_required
def project_detail(request, pk):
    """Project detail view with role-based access control"""
    project = get_object_or_404(Project, pk=pk)

    # Access Control Logic
    can_view = False
    if request.user.is_superuser:
        can_view = True
    elif request.user.is_staff:
        # Staff can see if they are advisor or co-advisor
        if project.advisor == request.user or project.co_advisor == request.user:
            can_view = True
    else:
        # Students can see only if they are members of the project
        if request.user in project.students.all():
            can_view = True

    if not can_view:
        messages.error(
            request, 'คุณไม่มีสิทธิ์เข้าถึงหรือดูข้อมูลของโครงงานนี้')
        return redirect('final_pro:project_list')

    evaluations = project.evaluations.all()
    requests = project.requests.all()
    submissions = project.submissions.all()

    # Define Workflow Steps
    workflow = [
        {'id': 1, 'name': 'ปรึกษาและเลือกอาจารย์', 'req': 'vt_1', 'eval': 'vt_p1'},
        {'id': 2, 'name': 'เสนอโครงร่างโครงงาน', 'req': 'vt_2', 'eval': 'vt_p2'},
        {'id': 3, 'name': 'รายงานความก้าวหน้า', 'req': 'vt_4', 'eval': 'vt_p3'},
        {'id': 4, 'name': 'สอบโครงงาน (จบ)', 'req': 'vt_5', 'eval': 'vt_p5'},
    ]

    current_step = 1
    # Logic to determine current step based on approved evaluations
    if evaluations.filter(form_type='vt_p5', is_approved=True).exists():
        current_step = 5  # Completed
    elif evaluations.filter(form_type='vt_p3', is_approved=True).exists():
        current_step = 4
    elif evaluations.filter(form_type='vt_p2', is_approved=True).exists():
        current_step = 3
    elif requests.filter(form_type='vt_1', status='approved').exists():
        current_step = 2

    context = {
        'project': project,
        'evaluations': evaluations,
        'requests': requests,
        'submissions': submissions,
        'workflow': workflow,
        'current_step': current_step,
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
    """Create request form with workflow validation"""
    project = get_object_or_404(Project, pk=project_pk)

    # Workflow Validation
    evaluations = project.evaluations.all()
    requests = project.requests.all()

    if request.method == 'POST':
        form = RequestFormSubmission(request.POST)
        if form.is_valid():
            f_type = form.cleaned_data['form_type']

            # Workflow check
            can_submit = True
            error_msg = ""

            # Steps: vt_1 -> vt_2 -> vt_4 -> vt_5
            if f_type == 'vt_2' and not requests.filter(form_type='vt_1', status='approved').exists():
                can_submit = False
                error_msg = "ต้องได้รับการตอบรับจากอาจารย์ (วท.1) และอนุมัติก่อนจึงจะยื่นเสนอโครงร่างได้"
            elif f_type == 'vt_4' and not evaluations.filter(form_type='vt_p2', is_approved=True).exists():
                can_submit = False
                error_msg = "ต้องผ่านการประเมินหัวข้อโครงงาน (วท.ป.2) ก่อนจึงจะรายงานความก้าวหน้าได้"
            elif f_type == 'vt_5' and not evaluations.filter(form_type='vt_p3', is_approved=True).exists():
                can_submit = False
                error_msg = "ต้องผ่านการประเมินความก้าวหน้า (วท.ป.3) ก่อนจึงจะขอสอบจบได้"

            if not can_submit:
                messages.error(request, error_msg)
                return render(request, 'request_form.html', {'form': form, 'project': project, 'title': 'ส่งแบบคำขอ'})

            request_form = form.save(commit=False)
            request_form.project = project
            request_form.submitted_by = request.user
            request_form.save()
            messages.success(
                request, 'ส่งคำขอสำเร็จ! กรุณารออาจารย์ตรวจสอบและประเมินผล')
            return redirect('final_pro:project_detail', pk=project.pk)
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


def export_project_docx(request, pk, form_type):
    """View to export project data to a Word document based on form type"""
    project = get_object_or_404(Project, pk=pk)

    # Map form types to file paths
    # Note: Using r"" for windows paths or forward slashes
    base_docs_path = os.path.join(settings.BASE_DIR, 'docs')

    template_map = {
        # แบบประเมิน
        'วท.ป.1': os.path.join(base_docs_path, 'แบบประเมิน', 'วท.ป.1 แบบประเมินกรอบของโครงงาน.docx'),
        'วท.ป.2': os.path.join(base_docs_path, 'แบบประเมิน', 'วท.ป.2 แบบประเมินการสอบหัวข้อโครงงาน.docx'),
        'วท.ป.5': os.path.join(base_docs_path, 'แบบประเมิน', 'วท.ป.5 แบบประเมินผลการการสอบโครงงาน.docx'),

        # แบบคำขอ (Most are .doc, only handling .docx for now with docxtpl)
        # Still .doc
        'วท.1': os.path.join(base_docs_path, 'แบบคำขอ', 'แบบคำขอ', 'วท.1 แบบคำขอเป็นที่ปรึกษา.doc'),
        'วท.รายงาน': os.path.join(base_docs_path, 'แบบคำขอ', 'แบบคำขอ', 'แบบรายงานการตรวจสอบเนื้อหาโครงงาน.docx'),
    }

    template_path = template_map.get(form_type)

    if not template_path:
        messages.error(request, f"ไม่พบเทมเพลตสำหรับ {form_type}")
        return redirect('final_pro:project_detail', pk=pk)

    if not template_path.endswith('.docx'):
        messages.error(
            request, f"เทมเพลต {form_type} ยังเป็นไฟล์ .doc ซึ่งไม่รองรับการ Generate อัตโนมัติ (กรุณาใช้ .docx)")
        return redirect('final_pro:project_detail', pk=pk)

    try:
        doc = generate_project_document(project, template_path)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename={form_type}_{project.id}.docx'

        doc.save(response)
        return response
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาดในการสร้างเอกสาร: {str(e)}")
        return redirect('final_pro:project_detail', pk=pk)


@login_required
def request_status_update(request, pk, status):
    """View for advisors to approve/reject requests"""
    if not request.user.is_staff:
        messages.error(request, 'เฉพาะอาจารย์เท่านั้นที่สามารถดำเนินการได้')
        return redirect('final_pro:home')

    request_form = get_object_or_404(RequestForm, pk=pk)
    request_form.status = status
    request_form.approved_by = request.user
    from django.utils import timezone
    request_form.processed_at = timezone.now()
    request_form.save()

    status_text = "อนุมัติ" if status == 'approved' else "ปฏิเสธ/ให้แก้ไข"
    messages.success(request, f'ดำเนินการ {status_text} สำเร็จ!')
    return redirect('final_pro:project_detail', pk=request_form.project.pk)


def register_view(request):
    """View for student registration"""
    if request.user.is_authenticated:
        return redirect('final_pro:home')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # Create User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                student_id=form.cleaned_data['student_id'],
                phone=form.cleaned_data['phone'],
                role='student'
            )

            messages.success(request, 'ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ')
            return redirect('final_pro:login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form': form})


def submission_success(request):
    """Success page after submission"""
    return render(request, 'submission_success.html')
