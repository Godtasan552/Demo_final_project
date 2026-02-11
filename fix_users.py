from final_pro.models import UserProfile, Project
from django.contrib.auth.models import User
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo_fipro.settings')
django.setup()


# Quick clean
User.objects.filter(username='somchai').delete()
User.objects.filter(username='mana').delete()

# Create Advisor (Staff/Superuser for demo stability)
u_admin = User.objects.create_superuser(
    username='somchai', email='somchai@example.com', password='password123')
u_admin.first_name = 'Somchai'
u_admin.last_name = 'Jaidee'
u_admin.save()
UserProfile.objects.create(
    user=u_admin, role='advisor', department='Information Technology')

# Create Student
u_student = User.objects.create_user(username='mana', password='password123')
u_student.first_name = 'Mana'
u_student.last_name = 'Chuchu'
u_student.save()
UserProfile.objects.create(user=u_student, role='student',
                           student_id='64010002', department='Information Technology')

print("SUCCESS: Users created")
