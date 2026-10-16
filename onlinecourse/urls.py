from django.urls import path
from . import views

urlpatterns = [
    path(
        "course/<int:course_id>/",
        views.course_details,
        name="course_details",
    ),
    path(
        "submit/<int:lesson_id>/",
        views.submit,
        name="submit",
    ),
    path(
        "result/<int:submission_id>/",
        views.show_exam_result,
        name="show_exam_result",
    ),
]
