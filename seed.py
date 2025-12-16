import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "noteeve.settings")
django.setup()

from notes.models import CustomUser, Subject, Topic, Note, Task, Bookmark, Progress


def run():
    print("🚀 Seeding dummy data...")

    # -----------------------------------------
    # 1. Create (or get) a user
    # -----------------------------------------
    user, created = CustomUser.objects.get_or_create(
        username="demo_user",
        defaults={
            "email": "demo@example.com",
            "role": "student",
            "password": "Demo@1234"
        }
    )
    if created:
        user.set_password("Demo@1234")
        user.save()

    print(f"👤 Using user: {user.username}")

    # Clear previous seed data
    Subject.objects.filter(owner=user).delete()
    Task.objects.filter(user=user).delete()
    Bookmark.objects.filter(user=user).delete()
    Progress.objects.filter(user=user).delete()

    # -----------------------------------------
    # 2. Create Subjects
    # -----------------------------------------
    subject_names = [
        "Data Structures",
        "Operating Systems",
        "Database Management",
        "Computer Networks",
        "Machine Learning"
    ]

    subjects = []

    for name in subject_names:
        s = Subject.objects.create(
            name=name,
            description=f"Auto-generated subject for {name}",
            owner=user
        )
        subjects.append(s)

    print("📘 Subjects created:", len(subjects))

    # -----------------------------------------
    # 3. Create Topics
    # -----------------------------------------
    topics = []
    for subject in subjects:
        for i in range(1, 5):
            t = Topic.objects.create(
                name=f"{subject.name} Topic {i}",
                description="Some topic description",
                subject=subject,
                order=i
            )
            topics.append(t)

    print("📚 Topics created:", len(topics))

    # -----------------------------------------
    # 4. Create Notes
    # -----------------------------------------
    notes = []
    for topic in topics:
        for i in range(1, 4):
            n = Note.objects.create(
                title=f"{topic.name} - Note {i}",
                content="This is dummy note content generated automatically.",
                topic=topic,
                owner=user,
                is_public=False
            )
            notes.append(n)

    print("📝 Notes created:", len(notes))

    # -----------------------------------------
    # 5. Create Tasks
    # -----------------------------------------
    for i in range(6):
        Task.objects.create(
            title=f"Task {i+1}",
            description="Auto-generated task.",
            user=user,
            completed=True if i < 3 else False
        )

    print("🗒️ Tasks created: 6")

    # -----------------------------------------
    # 6. Bookmarks
    # -----------------------------------------
    for i in range(5):
        Bookmark.objects.create(
            user=user,
            note=random.choice(notes),
            page_position=random.randint(0, 5)
        )
    print("🔖 Bookmarks created: 5")

    # -----------------------------------------
    # 7. Progress Data
    # -----------------------------------------
    for topic in topics:
        Progress.objects.create(
            user=user,
            topic=topic,
            completion_percentage=random.randint(20, 95)
        )

    print("📊 Progress values created")

    print("\n✨ Seeding complete! Your dashboard will look great now!")


if __name__ == "__main__":
    run()
