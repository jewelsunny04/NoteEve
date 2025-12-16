from django.contrib import admin
from .models import (
    CustomUser, Subject, Topic, Note, Bookmark, Task,
    Progress, Collaboration, Summary
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'date_joined')
    list_filter = ('role',)
    search_fields = ('username', 'email')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('name',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'order')
    list_filter = ('subject',)
    search_fields = ('name',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'owner', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'owner')
    search_fields = ('title', 'content')


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'created_at')
    list_filter = ('created_at', 'user')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'due_date', 'completed')
    list_filter = ('completed', 'due_date', 'user')
    search_fields = ('title',)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'completion_percentage', 'last_updated')
    list_filter = ('user', 'last_updated')


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'permission_level', 'created_at')
    list_filter = ('permission_level', 'created_at')


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('note', 'created_at')
    list_filter = ('created_at',)
