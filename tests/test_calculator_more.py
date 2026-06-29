import os
import pandas as pd
import pytest
from decimal import Decimal

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import Addition, Operation
from app.exceptions import ValidationError, OperationError
from app.exceptions import ConfigurationError
from app.calculation import Calculation
import pandas as pd


class DummyObserver:
    def __init__(self):
        self.updated = []

    def update(self, calculation):
        self.updated.append(calculation)


class BadOperation(Operation):
    def execute(self, a, b):
        raise RuntimeError('internal error')


def test_observer_add_remove_and_notify(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=cfg)
    obs = DummyObserver()
    calc.add_observer(obs)
    calc.set_operation(Addition())
    calc.perform_operation('1', '2')
    assert len(obs.updated) == 1
    calc.remove_observer(obs)
    calc.perform_operation('2', '3')
    assert len(obs.updated) == 1


def test_perform_raises_validation_error(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=cfg)
    calc.set_operation(Addition())
    with pytest.raises(ValidationError):
        calc.perform_operation('not_a_number', '1')


def test_perform_wraps_internal_exceptions(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=cfg)
    calc.set_operation(BadOperation())
    with pytest.raises(OperationError):
        calc.perform_operation('1', '2')


def test_save_history_empty_creates_file(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=cfg)
    # ensure history empty
    calc.clear_history()
    calc.save_history()
    assert cfg.history_file.exists()
    df = pd.read_csv(cfg.history_file)
    # file should have headers but no rows
    assert df.empty


def test_load_history_empty_file(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    # create empty csv with headers using pandas to ensure encoding matches
    cfg.history_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=['operation', 'operand1', 'operand2', 'result', 'timestamp']
                ).to_csv(cfg.history_file, index=False)

    calc = Calculator(config=cfg)
    # loading happens in __init__, but call explicitly to ensure branch
    calc.load_history()
    assert calc.history == []


def test_undo_redo_false_and_clear(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=cfg)
    assert calc.undo() is False
    assert calc.redo() is False
    calc.set_operation(Addition())
    calc.perform_operation('1', '1')
    calc.clear_history()
    assert calc.history == []
    assert calc.undo_stack == []
    assert calc.redo_stack == []


def test_setup_logging_failure(tmp_path, monkeypatch):
    # force logging.basicConfig to raise to hit the logging except branch
    monkeypatch.setenv('CALCULATOR_LOG_DIR', str(tmp_path / 'logs'))
    def bad_basicConfig(*args, **kwargs):
        raise RuntimeError('boom')
    monkeypatch.setattr('logging.basicConfig', bad_basicConfig)
    cfg = CalculatorConfig(base_dir=tmp_path)
    with pytest.raises(RuntimeError):
        Calculator(config=cfg)


def test_save_history_raises_when_to_csv_fails(tmp_path, monkeypatch):
    cfg = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=cfg)
    # add a calculation to history
    calc.history.append(Calculation('Addition', Decimal('1'), Decimal('2')))

    # make to_csv raise
    def bad_to_csv(*args, **kwargs):
        raise Exception('disk full')
    monkeypatch.setattr(pd.DataFrame, 'to_csv', bad_to_csv)
    with pytest.raises(OperationError):
        calc.save_history()


def test_load_history_raises_when_read_fails(tmp_path, monkeypatch):
    cfg = CalculatorConfig(base_dir=tmp_path)
    # create a dummy file so exists() is True
    cfg.history_dir.mkdir(parents=True, exist_ok=True)
    cfg.history_file.write_text('garbage')
    calc = Calculator(config=cfg)
    monkeypatch.setattr(pd, 'read_csv', lambda *a, **k: (_ for _ in ()).throw(Exception('bad')))
    with pytest.raises(OperationError):
        calc.load_history()


def test_calculation_unknown_operation_raises():
    with pytest.raises(OperationError):
        Calculation('UnknownOp', Decimal('1'), Decimal('2'))


def test_config_validate_raises():
    cfg = CalculatorConfig(base_dir=None)
    # force invalid values
    cfg.max_history_size = 0
    with pytest.raises(ConfigurationError):
        cfg.validate()
