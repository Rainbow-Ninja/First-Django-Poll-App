import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text = question_text, pub_date = time)

class QuestionModelTests(TestCase):
    # was_published_recently should return False if pub_date is in future
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    # was_published_recently returns False if published later than 1 day
    def test_was_published_recently_with_old_question(self):
        time = timezone.now() -  datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date = time)
        self.assertIs(old_question.was_published_recently(), False)

    # was_published_recently returns True id published within a day
    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() -  datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date = time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    # if no questions, show appropriate message
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    # questions with pub_date in the past are displayed on index page
    def test_past_question(self):
        create_question(question_text = "Past Question.", days = -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], 
            ['<Question: Past Question.>']
        )

    # questions with future pub_date are not displayed on index page
    def test_future_question(self):
        create_question(question_text = "Future Question.", days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    # if both future and past pub_date questions only one is displayed on page
    def test_future_question_and_past_question(self):
        create_question(question_text = "Past Question.", days = -30)
        create_question(question_text = "Future Question.", days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], 
            ['<Question: Past Question.>']
        )

    def test_two_past_questions(self):
        create_question(question_text = "Past Question 1.", days = -30)
        create_question(question_text = "Past Question 2.", days = -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], 
            ['<Question: Past Question 2.>', '<Question: Past Question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    # if only question is in future that 404 is found
    def test_future_question(self):
        future_question = create_question(future_question = "Future Question.", days = 5)
        url = reverse('polls:detail', args = (future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # if question pub_date is in ast that it can be seen
    def test_last_question(self):
        past_question = create_question(past_question = "Past Question.", days = -5)
        url = reverse('polls:detail', args = (past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response, past_question.question_text)
