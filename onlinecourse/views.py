from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import Course, Enrollment, Question, Choice, Submission


# -----------------------
# Course list + details
# -----------------------

class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.order_by('-pub_date')


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


# -----------------------
# Authentication
# -----------------------

def user_login(request):
    """
    Handles login from the navbar form in course_list_bootstrap.html.
    Template uses name="username" and name="psw"
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("psw")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
    return HttpResponseRedirect(reverse('onlinecourse:index'))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('onlinecourse:index'))


def registration(request):
    """
    Renders registration page on GET.
    Creates user + logs them in on POST.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("psw")
        firstname = request.POST.get("firstname", "")
        lastname = request.POST.get("lastname", "")
        email = request.POST.get("email", "")

        if username and password:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=firstname,
                last_name=lastname,
                email=email
            )
            login(request, user)
            return HttpResponseRedirect(reverse('onlinecourse:index'))

    return render(request, 'onlinecourse/registration_bootstrap.html')


# -----------------------
# Enrollment
# -----------------------

@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
    if created:
        enrollment.mode = Enrollment.AUDIT
        enrollment.save()

    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))


# -----------------------
# Exam submit + results
# -----------------------

def extract_answers(request):
    """
    Collect selected choice ids from POST payload.
    Template sends checkboxes like:
      name="choice_{{ choice.id }}" value="{{ choice.id }}"
    """
    submitted_answers = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            try:
                choice = Choice.objects.get(id=value)
                submitted_answers.append(choice)
            except Choice.DoesNotExist:
                pass
    return submitted_answers


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)

    choices = extract_answers(request)
    submission.choices.set(choices)

    submission_id = submission.id
    return HttpResponseRedirect(
        reverse(viewname='onlinecourse:exam_result', args=(course_id, submission_id,))
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    """
    Multiple-selection scoring:
    A question is correct ONLY if the selected choices match EXACTLY the correct choices.
    """
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)

    selected_choices = submission.choices.all()
    total_score = 0

    questions = course.question_set.all()
    for question in questions:
        correct_choices = question.choice_set.filter(is_correct=True)
        chosen_for_question = selected_choices.filter(question=question)

        if set(correct_choices) == set(chosen_for_question):
            total_score += question.grade

    context['course'] = course
    context['grade'] = total_score
    context['choices'] = selected_choices
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
