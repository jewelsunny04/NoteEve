from django import forms
from django.contrib.auth.forms import UserCreationForm
from tinymce.widgets import TinyMCE
from .models import CustomUser, Subject, Topic, Note, Task, Collaboration


# ============================
# Custom User Registration Form
# ============================
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')


# ============================
# Subject Form
# ============================
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


# ============================
# Topic Form
# ============================
class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('name', 'description', 'order')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# ============================
# Note Form (with TinyMCE)
# ============================
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('title', 'content', 'file_upload', 'is_public')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'file_upload': forms.FileInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ============================
# Task Form
# ============================
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'due_date', 'completed')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
