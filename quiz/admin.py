from django.contrib import admin
from .models import  Category, Quiz, Question, Choice, UserQuiz, Rating


admin.site.register(Category)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(UserQuiz)
admin.site.register(Rating)
