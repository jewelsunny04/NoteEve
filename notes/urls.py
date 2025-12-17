from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # ------------------------
    # SUBJECT ROUTES (ORDER FIXED)
    # ------------------------
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),


    # MUST COME BEFORE subject_detail
    path('subjects/<int:subject_id>/collaborators/',
         views.collaboration_manage,
         name='collaboration_manage'),

    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    # ------------------------
    # TOPICS
    # ------------------------
    path('topics/create/<int:subject_id>/', views.topic_create, name='topic_create'),
    path('topics/<int:pk>/edit/', views.topic_edit, name='topic_edit'),

    # ------------------------
    # NOTES
    # ------------------------
    # path('notes/create/<int:topic_id>/', views.note_create, name='note_create'),
    # path('notes/<int:pk>/', views.note_view, name='note_view'),
    # path('notes/<int:pk>/edit/', views.note_edit, name='note_edit'),
    # path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    # path('notes/', views.note_list, name='note_list'),
    # path('notes/<int:pk>/complete/', views.note_complete, name='note_complete'),
    
    path("notes/", views.note_list, name="note_list"),

    path("notes/create/<int:topic_id>/",
         views.note_create,
         name="note_create"),

    path("notes/<int:pk>/",
         views.note_view,
         name="note_view"),

    path("notes/<int:pk>/edit/",
         views.note_edit,
         name="note_edit"),

    path("notes/<int:pk>/delete/",
         views.note_delete,
         name="note_delete"),
    
    # ------------------------
    # BOOKMARKS
    # ------------------------
    path('bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('bookmarks/toggle/<int:note_id>/', views.bookmark_toggle, name='bookmark_toggle'),

    # ------------------------
    # TASKS
    # ------------------------
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),

    # ------------------------
    # PDF COMPILER
    # ------------------------
    path('pdf/compile/', views.pdf_compile, name='pdf_compile'),

    # ------------------------
    # AI SUMMARIZER
    # ------------------------
    path('summarizer/', views.summarizer, name='summarizer'),

    # ------------------------
    # PROGRESS API (Chart.js)
    # ------------------------
    path('api/progress/', views.progress_api, name='progress_api'),
]
