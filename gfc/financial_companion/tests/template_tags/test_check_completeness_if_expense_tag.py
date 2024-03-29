from .test_template_tag_base import TemplateTagTestCase
from financial_companion.templatetags import check_completeness_if_expense, get_completeness
from financial_companion.models import CategoryTarget, AbstractTarget


class CheckCompletenessIfExpenseTemplateTagTestCase(TemplateTagTestCase):
    """Test for the get_greggor_type_from_completeness logo template tag"""

    def setUp(self):
        self.income_target: AbstractTarget = CategoryTarget.objects.get(pk=1)
        self.expense_target: AbstractTarget = CategoryTarget.objects.get(pk=3)

    def test_income_completeness(self):
        completeness: float = get_completeness(self.income_target)
        checked_completeness = check_completeness_if_expense(
            completeness, self.income_target)
        self.assertEqual(checked_completeness, 0)

    def test_expense_completeness(self):
        completeness: float = get_completeness(self.expense_target)
        checked_completeness: float = check_completeness_if_expense(
            completeness, self.expense_target)
        self.assertEqual(checked_completeness, 100)

    def test_target_is_none(self):
        completeness: float = 100
        target: AbstractTarget = None
        checked_completeness: float = check_completeness_if_expense(
            completeness, target)
        self.assertEqual(checked_completeness, completeness)
