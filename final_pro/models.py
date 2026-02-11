from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    """Extended user profile for students and advisors"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    student_id = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(
        max_length=100, default='วิทยาการคอมพิวเตอร์')
    role = models.CharField(max_length=20, choices=[
        ('student', 'นักศึกษา'),
        ('advisor', 'อาจารย์ที่ปรึกษา'),
        ('committee', 'กรรมการ'),
    ], default='student')

    def __str__(self) -> str:
        # Get user's full name or username as fallback
        user_obj = self.user  # type: ignore
        full_name = user_obj.get_full_name() if hasattr(
            user_obj, 'get_full_name') else user_obj.username
        return f"{full_name} ({self.student_id or 'N/A'})"


class Project(models.Model):
    """Project/โครงงาน model"""
    STATUS_CHOICES = [
        ('draft', 'ร่าง'),
        ('proposal', 'เสนอโครงร่าง'),
        ('approved', 'อนุมัติแล้ว'),
        ('in_progress', 'กำลังดำเนินการ'),
        ('completed', 'เสร็จสิ้น'),
    ]

    title_th = models.CharField(
        max_length=255, verbose_name='ชื่อโครงงาน (ไทย)')
    title_en = models.CharField(
        max_length=255, verbose_name='ชื่อโครงงาน (อังกฤษ)', blank=True)
    description = models.TextField(verbose_name='รายละเอียด')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft')

    # Members
    students = models.ManyToManyField(
        User, related_name='projects_as_student', verbose_name='นักศึกษา')
    advisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                related_name='projects_as_advisor', verbose_name='อาจารย์ที่ปรึกษา')
    co_advisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='projects_as_co_advisor', verbose_name='อาจารย์ที่ปรึกษาร่วม')

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField(null=True, blank=True)
    expected_completion = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'โครงงาน'
        verbose_name_plural = 'โครงงาน'

    def __str__(self) -> str:
        return str(self.title_th)


class EvaluationForm(models.Model):
    """Evaluation forms (วท.ป.1 - วท.ป.5)"""
    FORM_TYPES = [
        ('vt_p1', 'วท.ป.1 แบบประเมินกรอบของโครงงาน'),
        ('vt_p2', 'วท.ป.2 แบบประเมินการสอบหัวข้อโครงงาน'),
        ('vt_p3', 'วท.ป.3 แบบประเมินผลความก้าวหน้าของโครงงาน'),
        ('vt_p3_1', 'วท.ป.3-1 แบบประเมินผลความก้าวหน้าของโครงงาน'),
        ('vt_p4', 'วท.ป.4 แบบประเมินผลการสอบโครงงาน'),
        ('vt_p5', 'วท.ป.5 แบบประเมินผลการสอบโครงงาน'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='evaluations')
    form_type = models.CharField(max_length=20, choices=FORM_TYPES)
    evaluator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='evaluations_given')

    # Common evaluation fields
    score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    comments = models.TextField(blank=True, verbose_name='ความเห็น')
    strengths = models.TextField(blank=True, verbose_name='จุดเด่น')
    improvements = models.TextField(blank=True, verbose_name='ข้อเสนอแนะ')

    # Status
    is_approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'แบบประเมิน'
        verbose_name_plural = 'แบบประเมิน'

    def __str__(self) -> str:
        # Pylint doesn't understand Django's get_FOO_display() and ForeignKey attributes
        # type: ignore
        return f"{self.get_form_type_display()} - {self.project.title_th}"


class RequestForm(models.Model):
    """Request forms (วท.1 - วท.14)"""
    FORM_TYPES = [
        ('vt_1', 'วท.1 แบบคำขอเป็นที่ปรึกษา'),
        ('vt_2', 'วท.2 คำขออนุมัติโครงร่างโครงงานและอาจารย์ที่ปรึกษา'),
        ('vt_3', 'วท.3 แบบขอสอบ - ขออนุมัติโครงงาน'),
        ('vt_4', 'วท.4 แบบรายงานความก้าวหน้าโครงงาน'),
        ('vt_5', 'วท.5 แบบขอสอบโครงงาน'),
        ('vt_6', 'วท.6 แบบขอเปลี่ยนอาจารย์ที่ปรึกษา'),
        ('vt_7', 'วท.7 แบบขอเปลี่ยนสมาชิกโครงงาน'),
        ('vt_9', 'วท.9 แบบทะเบียนประวัติผู้รับผิดชอบโครงงาน'),
        ('vt_10', 'วท.10 แบบเปลี่ยนขอบเขตโครงงาน'),
        ('vt_11', 'วท.11 แบบบันทึกการตรวจรูปแบบโครงงาน'),
        ('vt_12', 'วท.12 แบบขอเปลี่ยนหัวข้อโครงงาน'),
        ('vt_13', 'วท.13 ขออนุมัติเข้าเล่มโครงงาน'),
        ('vt_14', 'วท.14 แบบรับรองการตรวจเนื้อหาโครงงาน'),
    ]

    STATUS_CHOICES = [
        ('pending', 'รอพิจารณา'),
        ('approved', 'อนุมัติ'),
        ('rejected', 'ไม่อนุมัติ'),
        ('revision', 'ต้องแก้ไข'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='requests')
    form_type = models.CharField(max_length=20, choices=FORM_TYPES)
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='requests_submitted')

    # Request details
    request_details = models.TextField(verbose_name='รายละเอียดคำขอ')
    reason = models.TextField(blank=True, verbose_name='เหตุผล')

    # Status and approval
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests_approved')
    approval_note = models.TextField(
        blank=True, verbose_name='หมายเหตุการอนุมัติ')

    # Dates
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'แบบคำขอ'
        verbose_name_plural = 'แบบคำขอ'

    def __str__(self) -> str:
        # Pylint doesn't understand Django's get_FOO_display() and ForeignKey attributes
        # type: ignore
        return f"{self.get_form_type_display()} - {self.project.title_th}"


class Submission(models.Model):
    """Generic submission tracking"""
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='submissions')
    submission_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='submissions/', null=True, blank=True)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'การส่งงาน'
        verbose_name_plural = 'การส่งงาน'

    def __str__(self) -> str:
        # Pylint doesn't understand ForeignKey attributes
        return f"{self.title} - {self.project.title_th}"  # type: ignore
