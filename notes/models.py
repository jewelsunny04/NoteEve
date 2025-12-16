from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


# ============================
# Custom User Model
# ============================
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('provider', 'Content Provider'),
        ('student', 'Student'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# ============================
# Subject Model
# ============================
class Subject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subjects')

    collaborators = models.ManyToManyField(
        CustomUser,
        through='Collaboration',
        related_name='shared_subjects'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Dashboard + Subject List uses this
    progress = models.IntegerField(default=0)

    class Meta:
        db_table = 'subjects'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    # Auto update progress based on completed/read notes
    def update_progress(self, user):
        from .models import Note  # prevent circular import

        total_notes = Note.objects.filter(topic__subject=self, owner=user).count()
        completed = Note.objects.filter(
            topic__subject=self, owner=user, is_read=True).count()

        if total_notes == 0:
            self.progress = 0
        else:
            self.progress = int((completed / total_notes) * 100)

        self.save()


# ============================
# Topic Model
# ============================
class Topic(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')

    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'topics'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.subject.name} > {self.name}"


# ============================
# Note Model
# ============================
class Note(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    file_upload = models.FileField(upload_to='notes/', blank=True, null=True)

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='notes')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notes')

    is_public = models.BooleanField(default=False)

    # used for progress calculation
    is_read = models.BooleanField(default=False)

    # optional: task-style completion
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    # FIXED
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notes'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ============================
# Collaboration Model
# ============================
class Collaboration(models.Model):
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('edit', 'Can Edit'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    permission_level = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collaborations'
        unique_together = ['subject', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.subject.name}"


# ============================
# Bookmark Model
# ============================
class Bookmark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookmarks')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='bookmarks')

    page_position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarks'
        unique_together = ['user', 'note']

    def __str__(self):
        return f"{self.user.username} - {self.note.title}"


# ============================
# Task Model
# ============================
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')

    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tasks'
        ordering = ['due_date', '-created_at']

    def __str__(self):
        return self.title


# ============================
# Progress Model
# ============================
class Progress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)

    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'progress'

    def __str__(self):
        return f"{self.user.username} - {self.completion_percentage}%"


# ============================
# Summary Model
# ============================
class Summary(models.Model):
    note = models.OneToOneField(Note, on_delete=models.CASCADE, related_name='summary')
    summary_text = models.TextField()
    keywords = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'summaries'

    def __str__(self):
        return f"Summary - {self.note.title}"
