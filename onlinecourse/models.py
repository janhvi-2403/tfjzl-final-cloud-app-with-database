
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"


class Question(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_text = models.CharField(max_length=1000)

    def is_get_score(self, selected_ids):
        correct_ids = set(
            self.choices.filter(is_correct=True).values_list("id", flat=True)
        )
        selected_for_question = set(
            self.choices.filter(id__in=selected_ids).values_list("id", flat=True)
        )
        return bool(correct_ids) and correct_ids == selected_for_question

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    learner_name = models.CharField(max_length=150, default="Guest")
    answers = models.JSONField(default=dict, blank=True)
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.learner_name} - "
            f"{self.score}/{self.total_questions}"
        )


class Instructor(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class Learner(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name
