import importlib.util

from backend.app import config


def test_data_files_are_valid():
    spec = importlib.util.spec_from_file_location("validate_data", config.ROOT / "scripts" / "validate_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.schema_errors() == []
    assert module.reference_errors() == []
