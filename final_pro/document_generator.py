import os
from docxtpl import DocxTemplate


def generate_project_document(project, template_path):
    """
    Generates a docx document from a template file using project data.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}")

    doc = DocxTemplate(template_path)

    # Get all students
    students_list = project.students.all()
    student_names = ", ".join(
        [f"{s.user.get_full_name()}" for s in students_list])
    student_ids = ", ".join(
        [f"{s.profile.student_id}" for s in students_list if hasattr(s, 'profile')])

    context = {
        'project_title_th': project.title_th,
        'project_title_en': project.title_en,
        'description': project.description,
        'status': project.get_status_display(),
        'advisor_name': project.advisor.get_full_name() if project.advisor else "N/A",
        'co_advisor_name': project.co_advisor.get_full_name() if project.co_advisor else "N/A",
        'student_names': student_names,
        'student_ids': student_ids,
        'start_date': project.start_date.strftime('%d/%m/%Y') if project.start_date else "N/A",
        'expected_completion': project.expected_completion.strftime('%d/%m/%Y') if project.expected_completion else "N/A",
    }

    doc.render(context)
    return doc
