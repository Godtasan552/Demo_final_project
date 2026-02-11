import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from final_pro.models import UserProfile, Project, EvaluationForm, RequestForm


class Command(BaseCommand):
    help = 'Load sample data for the demo'

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing data...')
        Project.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating users...')

        # Create Advisors
        advisors = []
        advisor_names = [
            ('Somchai', 'Jaidee', 'somchai'),
            ('Somsak', 'Rakthai', 'somsak'),
            ('Wichai', 'Munkong', 'wichai'),
        ]

        for first, last, username in advisor_names:
            u = User.objects.create_user(
                username=username, password='password123', first_name=first, last_name=last, is_staff=True)
            profile = UserProfile.objects.create(
                user=u,
                role='advisor',
                department='Information Technology',
                phone=f'081-123-456{random.randint(0, 9)}'
            )
            advisors.append(u)

        # Create Students
        students = []
        student_names = [
            ('Kanya', 'Siri', 'kanya', '64010001'),
            ('Mana', 'Chuchu', 'mana', '64010002'),
            ('Piti', 'Raksak', 'piti', '64010003'),
            ('Chujai', 'Deejai', 'chujai', '64010004'),
            ('Somsri', 'Saensabai', 'somsri', '64010005'),
        ]

        for first, last, username, sid in student_names:
            u = User.objects.create_user(
                username=username, password='password123', first_name=first, last_name=last)
            profile = UserProfile.objects.create(
                user=u,
                role='student',
                student_id=sid,
                department='Information Technology'
            )
            students.append(u)

        self.stdout.write('Creating projects...')

        project_titles = [
            ('ระบบจัดการร้านอาหารอัจฉริยะ', 'Smart Restaurant Management System'),
            ('แอปพลิเคชันคัดแยกขยะด้วย AI', 'Waste Sorting Application using AI'),
            ('ระบบติดตามการเพาะปลูกในโรงเรือน',
             'Greenhouse Cultivation Monitoring System'),
            ('แพลตฟอร์มการเรียนรู้ออนไลน์สำหรับเด็ก',
             'Online Learning Platform for Kids'),
            ('ระบบจองคิวโรงพยาบาลผ่านเว็บ', 'Hospital Queue Booking System'),
        ]

        projects = []
        for th, en in project_titles:
            p = Project.objects.create(
                title_th=th,
                title_en=en,
                description=f'โครงการนี้มีเป้าหมายเพื่อพัฒนา {th} เพื่อช่วยอำนวยความสะดวกให้กับผู้ใช้งานทั่วไป',
                status=random.choice(['approved', 'in_progress', 'proposal']),
                advisor=random.choice(advisors),
                start_date=timezone.now().date() - timedelta(days=random.randint(30, 200)),
                expected_completion=timezone.now().date() + timedelta(days=random.randint(30, 200))
            )
            # Assign random students to the project
            p.students.set(random.sample(students, random.randint(1, 3)))
            projects.append(p)

        self.stdout.write('Creating forms...')

        # Add some evaluations to projects
        for p in projects:
            # Add 2 evaluations per project
            for _ in range(2):
                EvaluationForm.objects.create(
                    project=p,
                    form_type=random.choice(
                        ['วท.ป.1', 'วท.ป.2', 'วท.ป.3', 'วท.ป.4', 'วท.ป.5']),
                    evaluator=random.choice(advisors),
                    score=random.uniform(70, 95),
                    comments='ผลงานอยู่ในเกณฑ์ดี ควรปรับปรุงเรื่องความรวดเร็วของระบบเล็กน้อย',
                    strengths='การออกแบบ UI ทำได้ดีมาก มีฟีเจอร์ครบถ้วน',
                    improvements='เพิ่มความละเอียดในส่วนของ Security และ SQL Injection',
                    is_approved=random.choice([True, False])
                )

            # Add 1-2 requests per project
            for _ in range(random.randint(1, 2)):
                RequestForm.objects.create(
                    project=p,
                    form_type=random.choice(['วท.1', 'วท.2', 'วท.3', 'วท.14']),
                    submitted_by=p.students.all()[0],
                    request_details='ขอเปลี่ยนหัวข้อวิจัยเล็กน้อยเนื่องจากข้อมูลไม่เพียงพอ',
                    reason='แหล่งข้อมูลเดิมมีการเปลี่ยนแปลง API ทำให้ไม่สามารถดึงข้อมูลได้',
                    status=random.choice(['pending', 'approved', 'rejected'])
                )

        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded sample data for demo'))
