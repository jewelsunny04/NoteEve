NoteEve – AI-Enabled Smarter Notes

NoteEve is a full-stack Django application for managing academic notes with hierarchical organization, collaboration, task tracking, analytics, and AI-powered summarization.

The project focuses on clean backend architecture, role-based access control, file handling, and production-ready configuration.

🚀 Features
Core Functionality

User authentication with role support (Provider / Student)

Hierarchical structure: Subjects → Topics → Notes

Rich-text note editor (TinyMCE)

File uploads (PDF, text)

Public and private notes

Collaboration

Share subjects with other users

Permission levels: View / Edit

Controlled multi-user access

Productivity & Tracking

Task and to-do management with due dates

Progress tracking per subject and topic

Dashboard analytics with charts

Bookmarks for important notes

Advanced Features

Compile multiple notes into a single PDF

AI-based note summarization and keyword extraction

Django Admin for management and moderation

🧠 Tech Stack

Backend

Django 5.1+

Python 3.11+

PostgreSQL

Frontend

HTML5, CSS3

Bootstrap 5

JavaScript

Chart.js
Deployment

The project is deployment-ready and works with:

Gunicorn

PostgreSQL

Railway

Ensure:

DEBUG=False in production

Static files are collected

Proper environment variables are set

⚠️ Security Notes

.env is excluded from version control

Change SECRET_KEY before deployment

Use HTTPS in production

Do not commit credentials

📌 Project Intent

This project was built to demonstrate:

Real-world Django application structure

Role-based access control

File uploads and media handling

AI integration in a practical use case

Clean Git and deployment practices

🛣️ Future Enhancements

Real-time collaboration

Dark mode

OCR for scanned PDFs

Voice-to-text notes

Mobile client

Other Tools

TinyMCE (Rich Text Editor)

ReportLab (PDF Generation)

HuggingFace Transformers (AI Summarization)
