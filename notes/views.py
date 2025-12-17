import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .ai_utils import generate_summary
import requests

from .models import (
    CustomUser, Subject, Topic, Note, Bookmark, Task,
    Collaboration, Summary
)

from .forms import (
    CustomUserCreationForm, SubjectForm, TopicForm,
    NoteForm, TaskForm
)

# ============================================================
# AI SUMMARY HELPER
# ============================================================

# ============================================================
# HOME / AUTH
# ============================================================
def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data.get("role")
            user.save()

            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Please correct the errors.")
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
            messages.error(request, "Invalid username or password")

    return render(request, "notes/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")


# ============================================================
# DASHBOARD
# ============================================================
@login_required
def dashboard(request):
    user = request.user

    subjects = Subject.objects.filter(owner=user)
    subjects_count = subjects.count()

    notes = Note.objects.filter(owner=user)
    notes_count = notes.count()

    bookmarks_count = Bookmark.objects.filter(user=user).count()

    pending_tasks = Task.objects.filter(user=user, completed=False).count()

    recent_activity = [f"Added note: {n.title}" for n in notes[:3]]

    upcoming_tasks = Task.objects.filter(user=user, completed=False).order_by("due_date")[:3]

    return render(request, "notes/dashboard.html", {
        "subjects": subjects,
        "subjects_count": subjects_count,
        "notes_count": notes_count,
        "bookmarks_count": bookmarks_count,
        "pending_tasks": pending_tasks,
        "recent_activity": recent_activity,
        "upcoming_tasks": upcoming_tasks,
    })


# ============================================================
# SUBJECTS
# ============================================================

@login_required
def subject_list(request):
    user = request.user

    subjects = Subject.objects.filter(owner=user)
    shared_subjects = user.shared_subjects.all()

    # ---- Add computed fields ----
    for subject in subjects:
        notes = Note.objects.filter(topic__subject=subject, owner=user)

        subject.total_notes = notes.count()
        subject.completed_notes = notes.filter(is_completed=True).count()

        if subject.total_notes > 0:
            subject.progress = int((subject.completed_notes / subject.total_notes) * 100)
        else:
            subject.progress = 0

    for subject in shared_subjects:
        notes = Note.objects.filter(topic__subject=subject)

        subject.total_notes = notes.count()
        subject.completed_notes = notes.filter(is_completed=True).count()

        if subject.total_notes > 0:
            subject.progress = int((subject.completed_notes / subject.total_notes) * 100)
        else:
            subject.progress = 0

    return render(request, "notes/subject_list.html", {
        "subjects": subjects,
        "shared_subjects": shared_subjects,
    })

@property
def total_notes(self):
    return Note.objects.filter(topic__subject=self).count()

@property
def completed_notes(self):
    return Note.objects.filter(topic__subject=self, is_completed=True).count()
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


# ============================================================
# TOPICS
# ============================================================
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

    return render(request, "notes/topic_form.html", {"form": form, "subject": subject})


@login_required
def topic_edit(request, pk):
    topic = get_object_or_404(Topic, pk=pk, subject__owner=request.user)
    subject = topic.subject  # ✅ IMPORTANT

    if request.method == "POST":
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, "Topic updated!")
            return redirect("subject_detail", pk=subject.pk)
    else:
        form = TopicForm(instance=topic)

    return render(
        request,
        "notes/topic_form.html",
        {
            "form": form,
            "subject": subject,  # ✅ REQUIRED for template
            "topic": topic       # (optional but useful)
        }
    )



# ============================================================
# NOTES
# ============================================================
@login_required
def note_list(request):
    subjects = Subject.objects.filter(owner=request.user)
    selected_subject = request.GET.get("subject")

    if selected_subject:
        notes = Note.objects.filter(owner=request.user, topic__subject_id=selected_subject)
    else:
        notes = Note.objects.filter(owner=request.user)

    return render(request, "notes/note_list.html", {
        "notes": notes,
        "subjects": subjects,
        "selected_subject": int(selected_subject) if selected_subject else None,
    })

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

    return render(request, "notes/note_form.html", {"form": form, "topic": topic})


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

    return render(request, "notes/note_view.html", {"note": note, "bookmarked": bookmarked})


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


# ============================================================
# BOOKMARKS
# ============================================================
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


# ============================================================
# TASKS
# ============================================================
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


# ============================================================
# COLLABORATION (SHARING SUBJECTS)
# ============================================================
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


# ============================================================
# PDF COMPILER
# ============================================================
@login_required
def pdf_compile(request):
    if request.method == "POST":
        note_ids = request.POST.getlist("note_ids")
        notes = Note.objects.filter(pk__in=note_ids, owner=request.user)

        if not notes:
            messages.error(request, "No notes selected")
            return redirect("subject_list")

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from io import BytesIO

            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)

            y = 750
            for note in notes:
                pdf.setFont("Helvetica-Bold", 16)
                pdf.drawString(50, y, note.title)
                y -= 30

                pdf.setFont("Helvetica", 10)
                pdf.drawString(50, y, f"Subject: {note.topic.subject.name}")
                y -= 20

                pdf.drawString(50, y, f"Topic: {note.topic.name}")
                y -= 40

                if y < 100:
                    pdf.showPage()
                    y = 750

            pdf.save()
            buffer.seek(0)

            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename=\"compiled_notes.pdf\"'
            return response

        except Exception as e:
            messages.error(request, f"PDF error: {str(e)}")

    subjects = Subject.objects.filter(owner=request.user)
    return render(request, "notes/pdf_compile.html", {"subjects": subjects})

@login_required
def note_mark_read(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    note.is_read = True
    note.save()
    return redirect("note_list")
# ============================================================
# AI SUMMARIZER PAGE
# ============================================================
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
                    extracted_text += (page.extract_text() or "") + "\n"
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


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    topic = note.topic   # <--- ADD THIS

    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            return redirect("note_view", pk=note.pk)
    else:
        form = NoteForm(instance=note)

    return render(request, "notes/note_form.html", {
        "form": form,
        "topic": topic,  # <--- ADD THIS
    })

@login_required
def note_complete(request, pk):
    note = get_object_or_404(Note, pk=pk, topic__subject__owner=request.user)
    note.is_completed = True
    note.save()

    # Update subject progress automatically
    subject = note.topic.subject
    total_notes = Note.objects.filter(topic__subject=subject).count()
    completed = Note.objects.filter(topic__subject=subject, is_completed=True).count()

    if total_notes > 0:
        subject.progress = int((completed / total_notes) * 100)
        subject.save()

    messages.success(request, "Note marked as completed!")
    return redirect("note_view", pk=note.pk)
# ============================================================
# PROGRESS API (for charts)
# ============================================================
@login_required
def progress_api(request):
    user = request.user
    subjects = Subject.objects.filter(owner=user)

    return JsonResponse({
        "labels": [s.name for s in subjects[:5]],
        "data": [50 + i * 10 for i in range(len(subjects[:5]))],
    })
