from django.urls import path
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    # Course list + details
    path('', views.CourseListView.as_view(), name='index'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),

    # Enrollment
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),

    # Exam submit + result
    path('<int:course_id>/submit/', views.submit, name='submit'),
    path(
        'course/<int:course_id>/submission/<int:submission_id>/result/',
        views.show_exam_result,

        name='exam_result'
    ),

    # Auth routes (used by the navbar template tags)
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('registration/', views.registration, name='registration'),
]
