
from django.shortcuts import render, get_object_or_404, redirect

from .models import Course, Lesson, Enrollment, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    context = {
        "course": course,
    }

    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        context,
    )


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method != "POST":
        return redirect("course_details", course_id=course.id)

    lesson = get_object_or_404(
        Lesson,
        pk=request.POST.get("lesson_id"),
        course_id=course.id,
    )

    enrollment = None

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).first()

    questions = list(
        lesson.questions.prefetch_related("choices").all()
    )

    answers = {}

    for question in questions:
        choice_id = request.POST.get(f"question_{question.id}")

        if not choice_id:
            continue

        selected_choice = question.choices.filter(
            pk=choice_id
        ).first()

        if selected_choice:
            answers[str(question.id)] = selected_choice.id

    submission = Submission.objects.create(
        lesson=lesson,
        enrollment=enrollment,
        learner_name=(
            request.POST.get("learner_name", "").strip() or "Guest"
        ),
        answers=answers,
        score=0,
        total_questions=len(questions),
    )

    return redirect(
        "show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        lesson__course_id=course.id,
    )

    lesson = submission.lesson

    questions = list(
        lesson.questions.prefetch_related("choices").all()
    )

    selected_ids = list(submission.answers.values())

    results = []
    grade = 0

    for question in questions:
        selected_id = submission.answers.get(str(question.id))

        if selected_id is not None:
            selected_choice = question.choices.filter(
                pk=selected_id
            ).first()
        else:
            selected_choice = None

        correct_choice = question.choices.filter(
            is_correct=True
        ).first()

        is_correct = question.is_get_score(selected_ids)

        if is_correct:
            grade += 1

        results.append({
            "question": question,
            "selected_choice": selected_choice,
            "correct_choice": correct_choice,
            "is_correct": is_correct,
        })

    total_questions = len(questions)

    percentage = (
        round(grade * 100 / total_questions)
        if total_questions
        else 0
    )

    submission.score = grade
    submission.total_questions = total_questions

    submission.save(
        update_fields=["score", "total_questions"]
    )

    context = {
        "course": course,
        "lesson": lesson,
        "submission": submission,
        "results": results,
        "selected_ids": selected_ids,
        "grade": grade,
        "score": grade,
        "total_questions": total_questions,
        "percentage": percentage,
    }

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        context,
    )
