import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

import PyPDF2

from .models import (
    CustomUser, Subject, Topic, Note, Bookmark, Task,
    Collaboration
)

from .forms import (
    CustomUserCreationForm, SubjectForm, TopicForm,
    NoteForm, TaskForm
)

from .ai_utils import generate_summary


# ====================================
# AUTH / HOME
# ====================================

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()

    return render(request, "notes/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "notes/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")


# ====================================
# DASHBOARD
# ====================================

@login_required
def dashboard(request):
    user = request.user

    subjects = (
        Subject.objects.filter(owner=user) |
        Subject.objects.filter(collaboration__user=user)
    ).distinct()

    tasks = Task.objects.filter(user=user, completed=False).order_by("due_date")[:5]
    bookmarks = Bookmark.objects.filter(user=user)[:5]
    recent_notes = Note.objects.filter(owner=user).order_by("-created_at")[:5]

    total_notes = Note.objects.filter(owner=user).count()
    completed_tasks = Task.objects.filter(user=user, completed=True).count()

    return render(request, "notes/dashboard.html", {
        "subjects": subjects,
        "tasks": tasks,
        "bookmarks": bookmarks,
        "recent_notes": recent_notes,
        "total_notes": total_notes,
        "completed_tasks": completed_tasks,
    })


# ====================================
# SUBJECTS
# ====================================

@login_required
def subject_list(request):
    subjects = Subject.objects.filter(owner=request.user)
    shared_subjects = Subject.objects.filter(
        collaboration__user=request.user
    ).distinct()

    return render(request, "notes/subject_list.html", {
        "subjects": subjects,
        "shared_subjects": shared_subjects
    })


@login_required
def subject_create(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.owner = request.user
            subject.save()
            messages.success(request, "Subject created!")
            return redirect("subject_detail", pk=subject.pk)
    else:
        form = SubjectForm()

    return render(request, "notes/subject_form.html", {"form": form})


@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    if subject.owner != request.user:
        if not Collaboration.objects.filter(subject=subject, user=request.user).exists():
            messages.error(request, "Access denied")
            return redirect("subject_list")

    topics = subject.topics.all()

    return render(request, "notes/subject_detail.html", {
        "subject": subject,
        "topics": topics
    })


@login_required
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk, owner=request.user)

    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, "Subject updated!")
            return redirect("subject_detail", pk=pk)
    else:
        form = SubjectForm(instance=subject)

    return render(request, "notes/subject_form.html", {"form": form})


@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk, owner=request.user)

    if request.method == "POST":
        subject.delete()
        messages.success(request, "Subject deleted!")
        return redirect("subject_list")

    return render(request, "notes/subject_confirm_delete.html", {"subject": subject})


# ====================================
# TOPICS
# ====================================

@login_required
def topic_create(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, owner=request.user)

    if request.method == "POST":
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.subject = subject
            topic.save()
            messages.success(request, "Topic created!")
            return redirect("subject_detail", pk=subject_id)
    else:
        form = TopicForm()

    return render(request, "notes/topic_form.html", {
        "form": form,
        "subject": subject
    })


@login_required
def topic_edit(request, pk):
    topic = get_object_or_404(Topic, pk=pk, subject__owner=request.user)

    if request.method == "POST":
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, "Topic updated!")
            return redirect("subject_detail", pk=topic.subject.pk)
    else:
        form = TopicForm(instance=topic)

    return render(request, "notes/topic_form.html", {"form": form})


# ====================================
# NOTES
# ====================================

@login_required
def note_create(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id, subject__owner=request.user)

    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.topic = topic
            note.owner = request.user
            note.save()
            messages.success(request, "Note created!")
            return redirect("note_view", pk=note.pk)
    else:
        form = NoteForm()

    return render(request, "notes/note_form.html", {
        "form": form,
        "topic": topic
    })


@login_required
def note_view(request, pk):
    note = get_object_or_404(Note, pk=pk)

    if note.owner != request.user and not note.is_public:
        if not Collaboration.objects.filter(
            subject=note.topic.subject,
            user=request.user
        ).exists():
            messages.error(request, "Access denied")
            return redirect("subject_list")

    bookmarked = Bookmark.objects.filter(user=request.user, note=note).exists()

    return render(request, "notes/note_view.html", {
        "note": note,
        "bookmarked": bookmarked
    })


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)

    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated!")
            return redirect("note_view", pk=pk)
    else:
        form = NoteForm(instance=note)

    return render(request, "notes/note_form.html", {"form": form})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)

    if request.method == "POST":
        subject_id = note.topic.subject.pk
        note.delete()
        messages.success(request, "Note deleted!")
        return redirect("subject_detail", pk=subject_id)

    return render(request, "notes/note_confirm_delete.html", {"note": note})


# ====================================
# BOOKMARKS
# ====================================

@login_required
def bookmark_list(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, "notes/bookmark_list.html", {"bookmarks": bookmarks})


@login_required
@require_POST
def bookmark_toggle(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, note=note)

    if not created:
        bookmark.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "added"})


# ====================================
# TASKS
# ====================================

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by("due_date")
    return render(request, "notes/task_list.html", {"tasks": tasks})


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task created!")
            return redirect("task_list")
    else:
        form = TaskForm()

    return render(request, "notes/task_form.html", {"form": form})


@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    messages.success(request, "Task updated!")
    return redirect("task_list")


# ====================================
# COLLABORATION
# ====================================

@login_required
def collaboration_manage(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, owner=request.user)
    collaborations = Collaboration.objects.filter(subject=subject)

    if request.method == "POST":
        email = request.POST.get("collaborator_email")
        permission = request.POST.get("permission_level", "view")

        try:
            user = CustomUser.objects.get(email=email)
            collab, created = Collaboration.objects.get_or_create(
                subject=subject,
                user=user,
                defaults={"permission_level": permission}
            )
            if not created:
                collab.permission_level = permission
                collab.save()

            messages.success(request, f"Shared with {user.username}!")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found")

        return redirect("collaboration_manage", subject_id=subject_id)

    return render(request, "notes/collaboration.html", {
        "subject": subject,
        "collaborations": collaborations
    })


# ====================================
# PDF COMPILER
# ====================================

@login_required
def pdf_compile(request):
    if request.method == "POST":
        note_ids = request.POST.getlist("note_ids")
        notes = Note.objects.filter(pk__in=note_ids, owner=request.user)

        if not notes:
            messages.error(request, "No notes selected")
            return redirect("subject_list")

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        y = 750

        for note in notes:
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(50, y, note.title)
            y -= 40

            if y < 100:
                pdf.showPage()
                y = 750

        pdf.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="compiled_notes.pdf"'
        return response

    subjects = Subject.objects.filter(owner=request.user)
    return render(request, "notes/pdf_compile.html", {"subjects": subjects})


# ====================================
# AI SUMMARIZER (HUGGING FACE API)
# ====================================

@login_required
def summarizer(request):
    summary_output = None

    if request.method == "POST":
        user_text = request.POST.get("user_text", "")
        uploaded_file = request.FILES.get("pdf_file")

        extracted_text = ""

        if uploaded_file:
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
            except Exception:
                extracted_text = ""

        final_text = user_text.strip() if user_text.strip() else extracted_text.strip()

        if not final_text:
            summary_output = "No text found to summarize."
        else:
            summary_output = generate_summary(final_text)

    return render(request, "notes/summarizer.html", {
        "summary_output": summary_output
    })
