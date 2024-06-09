from django.urls import path
from .views import *

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', QuizCategoryView, basename='category')


urlpatterns = [
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),
    path('quizzes/create/', QuizCreateView.as_view(), name='quiz-create'),
    path('quizzes/<int:quiz_id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:quiz_id>/edit/', QuizEditView.as_view(), name='quiz-edit'),
    path('quizzes/<int:quiz_id>/delete/', QuizDeleteView.as_view(), name='quiz-delete'),
    path('quizzes/<int:quiz_id>/add-question/', AddQuestionToQuizView.as_view(), name='add-question'),
    path('quizzes/<int:quiz_id>/take/', TakeQuizView.as_view(), name='take-quiz'),
    path('categories/<int:category_id>/quizzes/', FilterQuizzesByCategoryView.as_view(), name='filter-quizzes'),
    

]
urlpatterns += router.urls