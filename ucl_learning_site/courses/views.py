from django.shortcuts import render
from django.views.generic import DetailView
from .models import Course, Module, Quiz, QuizAttempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
import math


# Create your views here.
class CourseDetailView(LoginRequiredMixin, DetailView):
    context_object_name = "curr_course"
    queryset = Course.objects.all()
    template_name = "pages/courses/course_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
        return context


class ModuleDetailView(LoginRequiredMixin, DetailView):
    context_object_name = "curr_module"
    queryset = Module.objects.all()
    template_name = "pages/courses/module_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
        context['curr_course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        if Quiz.objects.filter(module_id=self.kwargs['pk']).exists():
            quiz = get_object_or_404(Quiz, module_id=self.kwargs['pk'])
            context['quiz'] = quiz
            
            user = self.request.user
            try:
                quiz_attempt = user.quizattempt_set.get(quiz_id=quiz.id)
            except QuizAttempt.DoesNotExist:
                quiz_attempt = None
            context['quiz_attempt'] = quiz_attempt

        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        quiz = get_object_or_404(Quiz, module_id=self.kwargs['pk'])
        if request.POST.get('take_or_retake', '') == "retake":
            quiz_attempt = user.quizattempt_set.get(quiz_id=quiz.id)
            quiz_attempt.delete()
            user.quizattempt_set.create(quiz_id=quiz.id)
            return HttpResponseRedirect(
                reverse("courses:take-quiz", args=(self.kwargs["slug"], self.kwargs["pk"], quiz.id)))
        
        elif request.POST.get('take_or_retake', '') == 'take':
            user.quizattempt_set.create(quiz_id=quiz.id)
            return HttpResponseRedirect(
                reverse("courses:take-quiz", args=(self.kwargs["slug"], self.kwargs["pk"], quiz.id)))


class TakeQuizView(LoginRequiredMixin, DetailView):
    context_object_name = "quiz"
    template_name = "pages/courses/take_quiz.html"

    def get_queryset(self):
        return Quiz.objects.filter(module_id=self.kwargs["module_id"], id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
        context['curr_course'] = get_object_or_404(Course, slug=self.kwargs["course_slug"])
        return context

    def post(self, request, *args, **kwargs):
        # TODO check cases for missing fields
        user = self.request.user
        quiz = Quiz.objects.get(module_id=self.kwargs["module_id"], id=self.kwargs["pk"])
        quiz_attempt = user.quizattempt_set.get(quiz_id=self.kwargs["pk"])
        user_score = 0
        user_answers = []
        for question in quiz.question_set.all():
            curr_user_answer = request.POST.get(str(question.id))
            user_answers.append(curr_user_answer)
            if question.correct_answer == str(curr_user_answer):
                user_score += 1
        
        quiz_attempt.score = int(math.ceil((user_score*100) / quiz.get_question_count()))
        quiz_attempt.user_answers = user_answers

        quiz_attempt.save(update_fields=['score', 'user_answers', 'date_attempted'])

        return HttpResponseRedirect(
            reverse("courses:quiz-result", args=(self.kwargs["course_slug"], self.kwargs["pk"], quiz.id)))


class QuizResultView(LoginRequiredMixin, DetailView):
    context_object_name = "quiz"
    template_name = "pages/courses/quiz_result.html"

    def get_queryset(self):
        return Quiz.objects.filter(module_id=self.kwargs["module_id"], id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
        context['curr_course'] = get_object_or_404(Course, slug=self.kwargs["course_slug"])

        quiz_attempt = self.request.user.quizattempt_set.get(quiz_id=self.kwargs["pk"])
        questions = list(Quiz.objects.get(module_id=self.kwargs["module_id"], id=self.kwargs["pk"]).question_set.all())
        user_answers = list(quiz_attempt.user_answers)
        context['quiz_attempt'] = quiz_attempt
        context['question_and_answers'] = zip(questions, user_answers)
        return context


