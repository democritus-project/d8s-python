from collections import deque
from typing import Any

import pytest

from democritus_file_system import file_read, file_write
from democritus_strings import string_remove_from_start, string_remove_after

FILL_OUTPUT_SIGNAL = 'fill'
FILL_OUTPUT_SIGNAL_IN_CONTEXT = f'== {FILL_OUTPUT_SIGNAL.__repr__()}'
RAISES_OUTPUT_SIGNAL = 'raises'
RAISES_OUTPUT_SIGNAL_IN_CONTEXT = f'== {RAISES_OUTPUT_SIGNAL.__repr__()}'

fill_values = deque()


def pytest_assertrepr_compare(config, op: str, left: object, right: object):
    global fill_values

    if right == FILL_OUTPUT_SIGNAL:
        fill_values.append(left)
        pytest.skip(f'{op} {right.__repr__()}')


def _update_test(file_path: str, function_name: str, new_assertion_value: Any) -> bool:
    """Update the test with the given function_name in the file at the given file_path with the new_assertion_value."""
    from python_data import python_function_blocks

    test_file_content = file_read(file_path)
    original_function_block = function_block = [
        i for i in python_function_blocks(test_file_content) if function_name in i
    ][0]
    function_block = function_block.replace(FILL_OUTPUT_SIGNAL_IN_CONTEXT, f'== {new_assertion_value.__repr__()}', 1)
    test_file_content = test_file_content.replace(original_function_block, function_block, 1)
    return file_write(file_path, test_file_content)


def _update_test_with_error(file_path: str, function_name: str, error_type: str, erroneous_assertion: str) -> bool:
    """Update the test with the given function_name in the file at the given file_path with the new_assertion_value."""
    from python_data import python_function_blocks

    test_file_content = file_read(file_path)
    original_function_block = function_block = [
        i for i in python_function_blocks(test_file_content) if function_name in i
    ][0]
    # TODO: currently, the indentation of the new assertion is hard coded; eventually, I would like to get the indentation from the original assertion
    new_assertion = f'with pytest.raises({error_type}):\n        {erroneous_assertion}'
    full_erroneous_assertion = f'assert {erroneous_assertion} == \'{RAISES_OUTPUT_SIGNAL}\''
    function_block = function_block.replace(full_erroneous_assertion, new_assertion, 1)
    test_file_content = test_file_content.replace(original_function_block, function_block, 1)
    return file_write(file_path, test_file_content)


def _get_erroneous_call(report_text: str) -> str:
    """."""
    erroneous_line = [
        line for line in report_text.splitlines() if line.startswith('> ') and RAISES_OUTPUT_SIGNAL_IN_CONTEXT in line
    ][0]
    erroneous_assertion = erroneous_line.lstrip('> ')
    erroneous_assertion = string_remove_from_start(erroneous_assertion, 'assert ')
    erroneous_assertion = string_remove_after(erroneous_assertion, ' ==')
    erroneous_assertion = erroneous_assertion.rstrip('= ')
    return erroneous_assertion


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    global fill_values

    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    if rep.when == "call" and rep.skipped:
        if fill_values and (FILL_OUTPUT_SIGNAL_IN_CONTEXT in rep.longreprtext):
            file_path = rep.fspath
            function_name = item.name
            new_assertion_value = fill_values.popleft()
            _update_test(file_path, function_name, new_assertion_value)
    elif rep.when == 'call' and rep.failed:
        if RAISES_OUTPUT_SIGNAL_IN_CONTEXT in rep.longreprtext:
            print('here!!!')
            file_path = rep.fspath
            function_name = item.name
            error_type = rep.longreprtext.split(" ")[-1]
            erroneous_assertion = _get_erroneous_call(rep.longreprtext)
            _update_test_with_error(file_path, function_name, error_type, erroneous_assertion)
