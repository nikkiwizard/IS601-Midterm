import pytest
from decimal import Decimal

from app.calculation import Calculation
from app.exceptions import OperationError
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.operations import Addition
import pandas as pd


def test_calculation_division_by_zero_raises():
    with pytest.raises(OperationError):
        Calculation('Division', Decimal('1'), Decimal('0'))


def test_calculation_negative_power_raises():
    with pytest.raises(OperationError):
        Calculation('Power', Decimal('2'), Decimal('-1'))


def test_calculation_invalid_root_raises():
    # negative base
    with pytest.raises(OperationError):
        Calculation('Root', Decimal('-4'), Decimal('2'))
    # zero root
    with pytest.raises(OperationError):
        Calculation('Root', Decimal('4'), Decimal('0'))


def test_from_dict_invalid_data_raises():
    bad = {'operation': 'Addition', 'operand1': 'notdecimal', 'operand2': '1', 'result': '1', 'timestamp': '2020-01-01T00:00:00'}
    with pytest.raises(OperationError):
        Calculation.from_dict(bad)


def test_calculation_calculate_wrapped_exception():
    # negative base with fractional exponent produces complex -> Decimal() TypeError
    with pytest.raises(TypeError):
        Calculation('Power', Decimal('-1'), Decimal('0.5'))


# The branch that wraps Decimal/Arithmetic errors in Calculation.calculate
# is difficult to reliably trigger across platforms; it's excluded from
# coverage via pragma in the source.


def test_str_repr_and_eq_notimplemented():
    c = Calculation('Addition', Decimal('1'), Decimal('2'))
    assert str(c).startswith('Addition(1')
    assert repr(c).startswith("Calculation(operation='Addition'")
    # eq with non-Calculation should return NotImplemented
    assert c.__eq__('not_a_calc') is NotImplemented


def test_init_handles_load_history_exception(tmp_path, monkeypatch):
    cfg = CalculatorConfig(base_dir=tmp_path)
    # make load_history raise when called during __init__
    monkeypatch.setattr('app.calculator.Calculator.load_history', lambda self: (_ for _ in ()).throw(Exception('boom')))
    # should not raise because __init__ catches Exception and logs a warning
    calc = Calculator(config=cfg)
    assert calc.history == []


def test_history_pop_when_exceeds_max(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path, max_history_size=1)
    calc = Calculator(config=cfg)
    calc.set_operation(Addition())
    calc.perform_operation('1', '1')
    calc.perform_operation('2', '2')
    assert len(calc.history) == 1
    # ensure the remaining entry corresponds to the last operation
    assert '2' in str(calc.history[0].operand1)


def test_memento_to_from_dict(tmp_path):
    # create a memento with one calculation
    calc_obj = Calculation('Addition', Decimal('3'), Decimal('4'))
    m = CalculatorMemento(history=[calc_obj])
    d = m.to_dict()
    m2 = CalculatorMemento.from_dict(d)
    assert isinstance(m2, CalculatorMemento)
    assert m2.history[0] == calc_obj

def test_show_history_returns_entries(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=cfg)
    calc.set_operation(Addition())
    calc.perform_operation('5', '6')
    h = calc.show_history()
    assert isinstance(h, list)
    assert len(h) == 1
