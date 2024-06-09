from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from .models import *

from django.core.mail import send_mail
from django.conf import settings

from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet

class QuizCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_admin:
            return Response({'msg': 'Only admins can create quizzes'}, status=status.HTTP_403_FORBIDDEN)

        serializer = QuizSerializer(data=request.data)
        
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddQuestionToQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        if not request.user.is_admin:
            return Response({'msg': 'Only admins can add questions'}, status=status.HTTP_403_FORBIDDEN)

        quiz = Quiz.objects.get(id=quiz_id)
        questions_data = request.data
        print(request.data)
        for data in questions_data:
            choices_data = data.pop('choices')
            question_serializer = QuestionSerializer(data=data)
            if question_serializer.is_valid():
                question = question_serializer.save(quiz=quiz)
                for choice in choices_data:
                    choice['question'] = question.id
                    choice_serializer = ChoiceSerializer(data=choice)
                    if choice_serializer.is_valid():
                        choice_serializer.save()
                    else:
                        return Response(choice_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': 'Questions added successfully'}, status=status.HTTP_201_CREATED)

class QuizListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuizEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        if not request.user.is_admin:
            return Response({'msg': 'Only admins can edit quizzes'}, status=status.HTTP_403_FORBIDDEN)

        serializer = QuizSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        if not request.user.is_admin:
            return Response({'msg': 'Only admins can delete quizzes'}, status=status.HTTP_403_FORBIDDEN)

        quiz.delete()
        return Response({'msg': 'Quiz deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class QuizDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TakeQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        user = request.user
        user_quiz = UserQuiz.objects.create(user=user, quiz=quiz, score=0)
        total_score = 0
        for question_data in request.data.get('questions'):
            question = Question.objects.get(id=question_data.get('question_id'))
            selected_choice = Choice.objects.get(id=question_data.get('selected_choice_id'))
            if selected_choice.is_correct:
                total_score += question.points
        user_quiz.score = total_score
        user_quiz.save()
        # Send quiz result via email
        send_mail(
            'Quiz Result',
            f'You scored {total_score} in the quiz {quiz.title}.',
            settings.EMAIL_HOST_USER,
            [user.email]
        )
        return Response({'score': total_score}, status=status.HTTP_200_OK)

class UserProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_quizzes = UserQuiz.objects.filter(user=user)
        serializer = UserQuizSerializer(user_quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LeaderboardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, quiz_id):
        user_quizzes = UserQuiz.objects.filter(quiz__id=quiz_id).order_by('-score')[:10]
        serializer = UserQuizSerializer(user_quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuizCategoryView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class FilterQuizzesByCategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category_id):
        quizzes = Quiz.objects.filter(category__id=category_id)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        user = request.user
        rating, created = Rating.objects.get_or_create(quiz=quiz, user=user)
        serializer = RatingSerializer(rating, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AverageRatingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        average_rating = quiz.ratings.aggregate(Avg('rating'))['rating__avg']
        return Response({'average_rating': average_rating}, status=status.HTTP_200_OK)
