
from django.shortcuts import render, get_object_or_404, redirect

from .models import Course, Lesson, Submission


def course_details(request, course_id):
    """Display course details and its lessons."""
    course = get_object_or_404(Course, pk=course_id)

    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course},
    )


def submit(request, course_id):
    """Evaluate submitted exam answers and save the submission."""
    course = get_object_or_404(Course, pk=course_id)

    if request.method != "POST":
        return redirect("course_details", course_id=course.id)

    lesson_id = request.POST.get("lesson_id")

    lesson = get_object_or_404(
        Lesson,
        pk=lesson_id,
        course_id=course.id,
    )

    questions = list(
        lesson.questions.prefetch_related("choices").all()
    )

    answers = {}
    score = 0

    for question in questions:
        selected_id = request.POST.get(
            f"question_{question.id}"
        )

        if not selected_id:
            continue

        selected_choice = question.choices.filter(
            pk=selected_id
        ).first()

        if selected_choice:
            answers[str(question.id)] = selected_choice.id

            if selected_choice.is_correct:
                score += 1

    submission = Submission.objects.create(
        lesson=lesson,
        learner_name=(
            request.POST.get("learner_name", "").strip()
            or "Guest"
        ),
        answers=answers,
        score=score,
        total_questions=len(questions),
    )

    return redirect(
        "show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


def show_exam_result(request, course_id, submission_id):
    """Display the submitted exam result and answer review."""
    course = get_object_or_404(
        Course,
        pk=course_id,
    )

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        lesson__course_id=course.id,
    )

    lesson = submission.lesson

    questions = lesson.questions.prefetch_related(
        "choices"
    ).all()

    results = []

    for question in questions:
        selected_id = submission.answers.get(
            str(question.id)
        )

        selected_choice = None

        if selected_id is not None:
            selected_choice = question.choices.filter(
                pk=selected_id
            ).first()

        correct_choice = question.choices.filter(
            is_correct=True
        ).first()

        results.append(
            {
                "question": question,
                "selected_choice": selected_choice,
                "correct_choice": correct_choice,
                "is_correct": bool(
                    selected_choice
                    and selected_choice.is_correct
                ),
            }
        )

    total_questions = submission.total_questions

    percentage = (
        round(submission.score * 100 / total_questions)
        if total_questions
        else 0
    )

    context = {
        "course": course,
        "lesson": lesson,
        "submission": submission,
        "results": results,
        "score": submission.score,
        "total_questions": total_questions,
        "percentage": percentage,
    }

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        context,
    )
