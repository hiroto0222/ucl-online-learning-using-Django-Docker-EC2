from django.contrib import admin
import nested_admin
from . import models

# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',), }


class AnswerInLine(nested_admin.NestedStackedInline):
    model = models.Answer


class QuestionInline(nested_admin.NestedStackedInline):
    model = models.Question
    inlines = [AnswerInLine, ]


class QuizAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuestionInline, ]


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Module)
admin.site.register(models.Quiz, QuizAdmin)