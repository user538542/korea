from django.test import TestCase

from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
import time

# Create your tests here.
from .models import Board, Topic

# Тестирует значение параметра для всех объектов модели
def run_field_parameter_test(
        model, self_,
        field_and_parameter_value: dict,
        parameter_name: str) -> None:
    # Вначале мы получаем все объекты модели и проходимся по ним.
    # Дальше обходим словарь с полями и ожидаемыми значениями параметров.
    # После получаем реальные значения параметров, обращаясь к объекту.
    # А затем сравниваем их с ожидаемыми.
    for instance in model.objects.all():
        # Пример 1: field = "email"; expected_value = 256.
        # Пример 2: field = "email"; expected_value = "Электронная почта".
        for field, expected_value in field_and_parameter_value.items():
            parameter_real_value = getattr(
                instance._meta.get_field(field), parameter_name
            )
            self_.assertEqual(parameter_real_value, expected_value)

# Миксин для проверки verbose_name
# Мы создаём нужный метод и в нём вызываем нашу общую функцию с соответствующими параметрами.
# self.field_and_verbose_name и self.field_and_max_length берутся из класса, который наследуется от миксина.
# А именно – из метода setUpTestData класса ModelTest.
class TestVerboseNameMixin:
    # Метод, тестирующий verbose_name
    def run_verbose_name_test(self, model):
        if (model == Board):
            run_field_parameter_test(
                model, self, self.field_and_verbose_name_for_board, 'verbose_name'
            )
        if (model == Topic):
            run_field_parameter_test(
                model, self, self.field_and_verbose_name_for_topic, 'verbose_name'
            )

# Миксин для проверки max_length
class TestMaxLengthMixin:
    # Метод, тестирующий max_length
    def run_max_length_test(self, model):
        if (model == Board):
            run_field_parameter_test(
                model, self, self.field_and_max_length_for_board, 'max_length'
            )
        if (model == Topic):
            run_field_parameter_test(
                model, self, self.field_and_max_length_for_topic, 'max_length'
            )

# Наследуем класс ModelTest от наших миксинов.
class ModelTest(TestCase, TestVerboseNameMixin, TestMaxLengthMixin):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        Board.objects.create(name = 'Раздел №1', description = 'Описание для раздела №1')
        Topic.objects.create(subject='Тема №1', last_updated = datetime.now(), board_id = 1, starter_id = 1, views = 1)
    
        cls.field_and_verbose_name_for_board = {
            'name': _('board_name'),
            'description': _('board_description'),
        }

        cls.field_and_max_length_for_board = {
            'name': 128,
        }

        cls.field_and_verbose_name_for_topic = {
            'subject': _('topic_subject'),
            'last_updated': _('last_updated'),
            'views': _('views'),
        }

        cls.field_and_max_length_for_topic = {
            'subject': 255,
        }

    # Тест параметра verbose_name
    def test_verbose_name(self):        
        super().run_verbose_name_test(Board)
        super().run_verbose_name_test(Topic)

    # Тест параметра max_length
    def test_max_length(self):        
        super().run_max_length_test(Board)
        super().run_max_length_test(Topic)
