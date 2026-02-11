from django import forms
from .models import Project, EvaluationForm, RequestForm, Submission


class ProjectForm(forms.ModelForm):
    """Form for creating/editing projects"""
    class Meta:
        model = Project
        fields = ['title_th', 'title_en', 'description', 'status',
                  'advisor', 'co_advisor', 'start_date', 'expected_completion']
        widgets = {
            'title_th': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อโครงงาน (ภาษาไทย)'}),
            'title_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Title (English)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'รายละเอียดโครงงาน'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'advisor': forms.Select(attrs={'class': 'form-select'}),
            'co_advisor': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        expected_completion = cleaned_data.get('expected_completion')

        if start_date and expected_completion:
            if expected_completion < start_date:
                raise forms.ValidationError(
                    "วันที่กำหนดเสร็จต้องไม่มาก่อนวันที่เริ่มโครงงาน")
        return cleaned_data


class EvaluationFormSubmission(forms.ModelForm):
    """Form for submitting evaluation forms"""
    class Meta:
        model = EvaluationForm
        fields = ['form_type', 'score', 'comments',
                  'strengths', 'improvements']
        widgets = {
            'form_type': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'ความเห็นเพิ่มเติม'}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'จุดเด่นของโครงงาน'}),
            'improvements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ข้อเสนอแนะในการพัฒนา'}),
        }

    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score is not None:
            if score < 0 or score > 100:
                raise forms.ValidationError("คะแนนต้องอยู่ระหว่าง 0 ถึง 100")
        return score


class RequestFormSubmission(forms.ModelForm):
    """Form for submitting request forms"""
    class Meta:
        model = RequestForm
        fields = ['form_type', 'request_details', 'reason']
        widgets = {
            'form_type': forms.Select(attrs={'class': 'form-select'}),
            'request_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'รายละเอียดคำขอ'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'เหตุผลในการขอ'}),
        }


class SubmissionForm(forms.ModelForm):
    """Form for file submissions"""
    class Meta:
        model = Submission
        fields = ['submission_type', 'title', 'description', 'file']
        widgets = {
            'submission_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ประเภทการส่งงาน'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'หัวข้อ'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'รายละเอียด'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
