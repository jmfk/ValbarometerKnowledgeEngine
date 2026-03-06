import importlib
import pkgutil
from pathlib import Path


def load_all_test_cases():
    cases = []
    package_dir = Path(__file__).parent
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        if module_name.startswith("case_"):
            mod = importlib.import_module(f".{module_name}", package=__package__)
            cases.append(mod.TEST_CASE)
    return sorted(cases, key=lambda c: c["id"])


def load_test_case(case_id: str):
    for case in load_all_test_cases():
        if case["id"] == case_id:
            return case
    raise ValueError(f"Test case '{case_id}' not found")
