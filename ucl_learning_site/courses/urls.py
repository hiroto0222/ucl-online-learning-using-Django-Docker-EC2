from django.urls import path
from . import views


app_name = "courses"
urlpatterns = [
    path("<str:slug>/", views.CourseDetailView.as_view(), name="course-detail"),
    path("<str:slug>/<int:pk>/", views.ModuleDetailView.as_view(), name="module-detail"),
    path("<str:course_slug>/<int:module_id>/<int:pk>/", views.TakeQuizView.as_view(), name="take-quiz"),
    path("<str:course_slug>/<int:module_id>/<int:pk>/results/", views.QuizResultView.as_view(), name="quiz-result"),
]
