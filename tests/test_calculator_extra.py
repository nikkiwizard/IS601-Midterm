import pytest
from decimal import Decimal

import pandas as pd

from app.operations import (
    OperationFactory,
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Power,
    Root,
)
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError, OperationError


def test_operation_factory_create_and_unknown():
    op = OperationFactory.create_operation('add')
    assert isinstance(op, Addition)
    with pytest.raises(ValueError):
        OperationFactory.create_operation('unknown_op')


def test_basic_operations():
    a = Decimal('6')
    b = Decimal('3')
    assert Multiplication().execute(a, b) == Decimal('18')
    assert Subtraction().execute(a, b) == Decimal('3')
    assert Addition().execute(a, b) == Decimal('9')


def test_division_by_zero_validation():
    with pytest.raises(ValidationError):
        Division().execute(Decimal('1'), Decimal('0'))


def test_power_negative_exponent():
    with pytest.raises(ValidationError):
        Power().execute(Decimal('2'), Decimal('-1'))


def test_root_invalid():
    with pytest.raises(ValidationError):
        Root().execute(Decimal('-4'), Decimal('2'))
    with pytest.raises(ValidationError):
        Root().execute(Decimal('4'), Decimal('0'))


def test_calculator_perform_and_history_and_undo_redo(tmp_path, monkeypatch):
    # Ensure calculator uses the temporary paths, not any repo/global files
    monkeypatch.setenv('CALCULATOR_HISTORY_DIR', str(tmp_path / 'history'))
    monkeypatch.setenv('CALCULATOR_HISTORY_FILE', str(tmp_path / 'history' / 'calculator_history.csv'))
    monkeypatch.setenv('CALCULATOR_LOG_DIR', str(tmp_path / 'logs'))
    monkeypatch.setenv('CALCULATOR_LOG_FILE', str(tmp_path / 'logs' / 'calculator.log'))

    cfg = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=cfg)
    with pytest.raises(OperationError):
        calc.perform_operation('1', '1')

    op = OperationFactory.create_operation('add')
    calc.set_operation(op)
    res = calc.perform_operation('1', '2')
    assert res == Decimal('3')
    assert len(calc.history) == 1

    # undo
    assert calc.undo() is True
    assert len(calc.history) == 0

    # redo
    assert calc.redo() is True
    assert len(calc.history) == 1

    # save history and verify file
    calc.save_history()
    assert cfg.history_file.exists()
    df = pd.read_csv(cfg.history_file)
    assert 'operation' in df.columns

    # get_history_dataframe
    df2 = calc.get_history_dataframe()
    assert not df2.empty
