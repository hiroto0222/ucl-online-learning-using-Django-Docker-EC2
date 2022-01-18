from http.client import MULTIPLE_CHOICES
import textwrap
from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()

# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(default=title)
    description = RichTextField(config_name = 'default', external_plugin_resources=[(
        'mathjax',
        '/static/ckeditor/ckeditor/plugins/mathjax/',
        'plugin.js',
    )])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_modules(self):
        return self.module_set.all()

    def get_course_title(self):
        words = textwrap.wrap(self.title, 20)
        if len(words) > 1:
            words[0] += "\n"
        return "".join(words)
    
    def get_absolute_url(self):
        return reverse("courses:course-detail", kwargs={"slug": self.slug})
    


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    content = RichTextField(config_name = 'default', external_plugin_resources=[(
        'mathjax',
        '/static/ckeditor/ckeditor/plugins/mathjax/',
        'plugin.js',
    )])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.course.title + ": " + self.title

    def get_absolute_url(self):
        return reverse("courses:module-detail", kwargs={"slug": self.course.slug, "pk": self.id})


class Quiz(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    instructions = models.CharField(max_length=255)
    pass_percentage = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.module) + " - " + self.title
    
    def get_question_count(self):
        return self.question_set.all().count()


class Question(models.Model):
    MULTIPLE_CHOICE = 'MCQ'
    USER_INPUT = 'UIQ'
    QUESTION_TYPES = [
        (MULTIPLE_CHOICE, 'Multiple Choice Question'),
        (USER_INPUT, 'User Input Question'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    question_type = models.CharField(
        max_length=3,
        choices=QUESTION_TYPES,
        default=MULTIPLE_CHOICE,
    )
    prompt = RichTextField(config_name='default', external_plugin_resources=[(
        'mathjax',
        '/static/ckeditor/ckeditor/plugins/mathjax/',
        'plugin.js',
    )])
    correct_answer = models.CharField(default="", max_length=255)

    class Meta:
        ordering = ['order', ]

    def __str__(self):
        return self.quiz.title + ": Question " + str(self.order)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    text = models.CharField(max_length=255)

    class Meta:
        ordering = ['order', ]
    
    def __str__(self):
        return str(self.question) + ": Answer " + str(self.order)


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    user_answers = ArrayField(
        base_field=models.CharField(max_length=255),
        default=list,
    )
    is_completed = models.BooleanField(default=False)
    date_attempted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ", quiz: " + self.quiz.title

    def passed(self):
        return self.score >= self.quiz.pass_percentage

    def get_date_attempted(self):
        return self.date_attempted.strftime('%B %d %Y')
