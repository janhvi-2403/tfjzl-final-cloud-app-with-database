
from django.contrib import admin

from .models import (
    Course,
    Lesson,
    Instructor,
    Learner,
    Question,
    Choice,
    Submission,
)


class ChoiceInline(admin.TabularInline):
    """Display choices inside the question admin page."""
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    """Display questions inside the lesson admin page."""
    model = Question
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    """Configure the question administration page."""
    list_display = ("question_text", "lesson")
    inlines = [ChoiceInline]


class LessonAdmin(admin.ModelAdmin):
    """Configure the lesson administration page."""
    list_display = ("title", "course")
    inlines = [QuestionInline]


# Register models with Django Admin.
admin.site.register(Course)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
