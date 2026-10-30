import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path
from unittest.mock import Mock

from gera1.orchestrator.application import TobyApplication, TobyReadCommand
from gera1.orchestrator.demo import run_synthetic_demo
from gera1.orchestrator.toby import synthesize
from gera1.strands.finance.models import AffordabilityResult, ResultStatus as FStatus
from gera1.strands.operations.models import UpcomingCommitmentsResult, ResultStatus as CStatus
from gera1.strands.inventory.models import IngredientAvailabilityResult, IngredientAssessment, AvailabilityStatus, ResultStatus as IStatus
from decimal import Decimal


def sample():
    f = AffordabilityResult('f', 'synthetic', FStatus.OK, 'finance_only', 'GBP', True, 'ok',
                            {'remaining_minor': 1500}, audit_id='fa')
    c = UpcomingCommitmentsResult('c', 'synthetic', CStatus.OK, 'calendar', 'GBP', 'ok',
                                   date(2026, 9, 26), date(2026, 9, 30), audit_id='ca')
    item = IngredientAssessment('eggs', 'Eggs', Decimal(12), 'each', 'each', Decimal(0),
                                Decimal(0), Decimal(0), Decimal(12), AvailabilityStatus.SHORTAGE,
                                ('stock:eggs',))
    i = IngredientAvailabilityResult('i', 'synthetic', IStatus.OK, 'inventory', 'shortage',
                                     items=(item,), audit_id='ia')
    return f, c, i


class TobyTest(unittest.TestCase):
    def test_synthetic_three_specialist_chain_reaches_model_with_unknowns(self):
        stock = Path(__file__).resolve().parents[1] / 'data/fixtures/bobathan_ingredient_stock_case.json'
        model = Mock()
        model.complete.return_value = 'Cannot confirm: eggs short, butter unknown, capacity unchecked.'
        answer = run_synthetic_demo(stock_data=stock, model=model)
        self.assertEqual(answer.recommendation, 'cannot_confirm')
        self.assertTrue(answer.model_used)
        facts = model.complete.call_args.args[1]
        self.assertIn('remaining pence=1500', facts)
        self.assertIn('Large eggs', facts)
        self.assertIn('Unsalted butter', facts)
        self.assertIn('production_capacity', answer.missing)

    def test_unknowns_and_shortage_never_become_approval(self):
        f, c, i = sample()
        model = Mock()
        model.complete.return_value = 'The customer can have the order.'
        answer = synthesize(business_id='synthetic', finance=f, calendar=c,
                            inventory=i, model=model)
        self.assertEqual(answer.recommendation, 'cannot_confirm')
        self.assertIn('ingredient_shortage', answer.missing)
        self.assertIn('production_capacity', answer.missing)
        self.assertTrue(answer.model_used)
        self.assertIn('cannot_confirm', model.complete.call_args.args[1])

    def test_cross_business_or_denied_result_never_reaches_model(self):
        f, c, i = sample()
        model = Mock()
        for changed in (replace(i, business_id='other'), replace(i, status=IStatus.DENIED)):
            answer = synthesize(business_id='synthetic', finance=f, calendar=c,
                                inventory=changed, model=model)
            self.assertEqual(answer.recommendation, 'blocked')
        model.complete.assert_not_called()

    def test_application_stops_before_later_reads_on_denial(self):
        f, _, _ = sample()
        saul, galgali, bobathan, model = (Mock() for _ in range(4))
        saul.check_affordability.return_value = replace(f, status=FStatus.DENIED)
        command = TobyReadCommand('r', 'actor', 'synthetic', Path('f'), Path('c'), Path('i'),
                                  'p', date(2026,9,26), date(2026,9,30))
        answer = TobyApplication(saul=saul, galgali=galgali,
                                 bobathan=bobathan, model=model).review(command)
        self.assertEqual(answer.recommendation, 'blocked')
        galgali.list_financial_calendar.assert_not_called()
        bobathan.check_ingredient_stock.assert_not_called()
        model.complete.assert_not_called()

    def test_provider_error_falls_back_without_approval(self):
        f, c, i = sample()
        model = Mock()
        model.complete.side_effect = TimeoutError()
        answer = synthesize(business_id='synthetic', finance=f, calendar=c,
                            inventory=i, model=model)
        self.assertFalse(answer.model_used)
        self.assertEqual(answer.recommendation, 'cannot_confirm')
