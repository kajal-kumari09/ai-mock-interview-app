from django.urls import path

from .views import home, quiz_session, speak_question

app_name = "quiz"

urlpatterns = [
    path("", home, name="home"),
    path("api/quiz-session/", quiz_session, name="quiz_session"),
    path("api/speak-question/", speak_question, name="speak_question"),
]
