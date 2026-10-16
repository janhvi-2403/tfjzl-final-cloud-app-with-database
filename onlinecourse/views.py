from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Question, Choice, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course},
    )


def submit(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)

    if request.method != "POST":
        return redirect("course_details", course_id=lesson.course_id)

    questions = lesson.questions.prefetch_related("choices").all()
    answers = {}
    score = 0

    for question in questions:
        selected_id = request.POST.get(f"question_{question.id}")

        if selected_id:
            choice = question.choices.filter(pk=selected_id).first()

            if choice:
                answers[str(question.id)] = choice.id
                if choice.is_correct:
                    score += 1

    submission = Submission.objects.create(
        lesson=lesson,
        learner_name=request.POST.get("learner_name", "").strip() or "Guest",
        answers=answers,
        score=score,
        total_questions=questions.count(),
    )

    return redirect("show_exam_result", submission_id=submission.id)


def show_exam_result(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    questions = submission.lesson.questions.prefetch_related("choices").all()

    results = []
    for question in questions:
        selected_id = submission.answers.get(str(question.id))
        selected_choice = question.choices.filter(pk=selected_id).first()
        correct_choice = question.choices.filter(is_correct=True).first()

        results.append({
            "question": question,
            "selected_choice": selected_choice,
            "correct_choice": correct_choice,
            "is_correct": bool(
                selected_choice and selected_choice.is_correct
            ),
        })

    percentage = (
        round(submission.score * 100 / submission.total_questions)
        if submission.total_questions else 0
    )

    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "submission": submission,
            "results": results,
            "percentage": percentage,
        },
    )
