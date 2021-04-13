import inspect
import os

import pytest
from d8s_file_system import directory_create, directory_delete, file_read, file_write

from d8s_python import (
    python_clean,
    python_code_details,
    python_copy_deep,
    python_disassemble,
    python_file_names,
    python_files_using_function,
    python_fstrings,
    python_function_blocks,
    python_function_lengths,
    python_functions_signatures,
    python_is_version_2,
    python_is_version_3,
    python_keywords,
    python_line_count,
    python_make_pythonic,
    python_namespace_has_argument,
    python_object_doc_string,
    python_object_module,
    python_object_properties_enumerate,
    python_object_signature,
    python_object_source_code,
    python_object_source_file,
    python_object_type_to_word,
    python_sort_type_list_by_name,
    python_stack_local_data,
    python_todos,
    python_traceback_prettify,
    python_traceback_pretty_print,
    python_version,
)

from .test_ast_data import TEST_CODE_WITH_ASYNC_FUNCTION, TEST_CODE_WITH_NESTED_FUNCTION

PYTHON_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../d8s_python/python_data.py'))
PYTHON_FILE_TEXT = file_read(PYTHON_FILE_PATH)
SIMPLE_FUNCTION = '''def test(a) -> List:
    print(a)

    return []'''


TEST_DIRECTORY_PATH = './test_files'
TEST_FILE_CONTENTS = 'def a():\n    return 1'
TEST_FILE_NAME_1 = 'a.py'
TEST_FILE_NAME_2 = 'a_test.py'
EXISTING_FILE_PATH_1 = os.path.join(TEST_DIRECTORY_PATH, TEST_FILE_NAME_1)
EXISTING_FILE_PATH_2 = os.path.join(TEST_DIRECTORY_PATH, TEST_FILE_NAME_2)


@pytest.fixture(autouse=True)
def clear_testing_directory():
    """This function is run after every test."""
    directory_delete(TEST_DIRECTORY_PATH)
    directory_create(TEST_DIRECTORY_PATH)
    file_write(EXISTING_FILE_PATH_1, TEST_FILE_CONTENTS)
    file_write(EXISTING_FILE_PATH_2, TEST_FILE_CONTENTS)


def setup_module():
    """This function is run before all of the tests in this file are run."""
    directory_create(TEST_DIRECTORY_PATH)


def teardown_module():
    """This function is run after all of the tests in this file are run."""
    directory_delete(TEST_DIRECTORY_PATH)


def test_python_object_signature_1():
    result = python_object_signature(python_object_signature)
    assert isinstance(result, inspect.Signature)


def test_python_object_source_code_1():
    result = python_object_source_code(python_object_signature)
    print(f'result: {result}')
    assert (
        result
        == 'def python_object_signature(python_object: Any) -> str:\n    """Get the argument signature for the given python object (e.g. module, function, or class)."""\n    import inspect\n\n    return inspect.signature(python_object)\n'
    )


def test_python_function_lengths_1():
    result = python_function_lengths(SIMPLE_FUNCTION)
    assert result == [3]


def test_python_line_count_1():
    result = python_line_count(SIMPLE_FUNCTION)
    assert result == 3

    result = python_line_count(SIMPLE_FUNCTION, ignore_empty_lines=False)
    assert result == 4


def test_python_todos_1():
    s = '''# TODO: hi!'''
    result = python_todos(s)
    assert result == ['TODO: hi!']

    s = '''# todo: hi!'''
    result = python_todos(s)
    assert result == []

    s = '''# todo: hi!'''
    result = python_todos(s, 'todo:.*')
    assert result == ['todo: hi!']


def test_python_stack_local_data_docs_1():
    result = python_stack_local_data()
    assert isinstance(result, dict)
    assert 'inspect' in result


def test_python_code_details_docs_1():
    result = python_code_details(SIMPLE_FUNCTION)
    assert result.startswith(
        '''Name:              <module>
Filename:          <disassembly>
'''
    )


def test_python_disassemble_docs_1():
    result = python_disassemble(SIMPLE_FUNCTION)
    print(f'result {result} ')
    assert result.strip().startswith(
        '''1           0 LOAD_NAME                0 (List)
              2 LOAD_CONST               0 (('return',))
              4 BUILD_CONST_KEY_MAP      1
              6 LOAD_CONST               1'''
    )


def test_python_copy_deep_docs_1():
    # make a list, make a copy of the list, modify the original list and the copy, and make sure that the lists are modified independently of one another
    l = [2, 3, 5, 7]
    result = python_copy_deep(l)
    l.pop(0)
    result.append(11)
    assert l == [3, 5, 7]
    assert result == [2, 3, 5, 7, 11]


def test_python_object_properties_enumerate_docs_1(capsys):
    s = 'foo'
    python_object_properties_enumerate(s)
    captured = capsys.readouterr()
    assert captured.out
    assert 'upper: FOO' in captured.out
    assert "__getattribute__: <method-wrapper '__getattribute__' of str object" in captured.out

    s = 'foo'
    python_object_properties_enumerate(s, run_methods=False)
    captured = capsys.readouterr()
    assert captured.out
    assert 'upper: FOO' not in captured.out
    assert "__getattribute__: <method-wrapper '__getattribute__' of str object" in captured.out

    s = 'foo'
    python_object_properties_enumerate(s, internal_properties=False)
    captured = capsys.readouterr()
    assert captured.out
    assert 'upper: FOO' in captured.out
    assert "__getattribute__: <method-wrapper '__getattribute__' of str object" not in captured.out

    s = 'foo'
    python_object_properties_enumerate(s, run_methods=False, internal_properties=False)
    captured = capsys.readouterr()
    assert captured.out
    assert 'upper: FOO' not in captured.out
    assert "__getattribute__: <method-wrapper '__getattribute__' of str object" not in captured.out


def test_python_version_docs_1():
    result = python_version()
    assert isinstance(result, str)
    assert result.startswith('3.')


def test_python_clean_docs_1():
    s = '''>>> import argparse
>>> args = argparse.Namespace()
>>> args.foo = 1'''
    result = python_clean(s)
    assert (
        result
        == '''import argparse
args = argparse.Namespace()
args.foo = 1'''
    )


def test_python_namespace_has_argument_docs_1():
    import argparse

    namespace = argparse.Namespace()
    namespace.foo = 1
    assert python_namespace_has_argument(namespace, 'foo')
    assert not python_namespace_has_argument(namespace, 'bar')


def test_python_object_doc_string_docs_1():
    def a():
        """Foo bar."""
        return 1

    result = python_object_doc_string(a)
    assert result == 'Foo bar.'

    def a():
        return 1

    result = python_object_doc_string(a)
    assert result is None


def test_python_functions_signatures_docs_1():
    s = '''def string_remove_numbers(input_string: str, replacement: str = ' ') -> str:
    """Remove all numbers from the input_strings."""
    new_string_without_numbers = replace('\\d+', replacement, input_string)
    return new_string_without_numbers'''
    results = python_functions_signatures(s)
    print(f'results {results} ')
    assert results == ["(input_string: str, replacement: str = ' ') -> str"]

    s = '''def python_functions_signatures(
    code_text: str, ignore_private_functions: bool = False, keep_function_name: bool = False
) -> ListOfStrs:
    print('hi')'''
    results = python_functions_signatures(s)
    assert results == [
        '(\n    code_text: str, ignore_private_functions: bool = False, keep_function_name: bool = False\n) -> ListOfStrs'
    ]

    s = '''@decorators.map_first_arg
def indefinite_article(word):
    """Return the word(s) with the appropriate indefinite article."""
    inflect_engine = _inflect_engine()
    return inflect_engine.a(word).split(' ')[0]


@decorators.map_first_arg
def plural(word, count=None):
    """Make the word(s) plural."""
    inflect_engine = _inflect_engine()
    return inflect_engine.plural(word, count=count)'''
    results = python_functions_signatures(s)
    print(f'results {results} ')
    assert results == ['(word)', '(word, count=None)']

    results = python_functions_signatures(SIMPLE_FUNCTION)
    print(f'results {results} ')
    assert results == ['(a) -> List']

    results = python_functions_signatures(SIMPLE_FUNCTION, keep_function_name=True)
    print(f'results {results} ')
    assert results == ['test(a) -> List']


def test_python_functions_signatures__ignore_nested_functions():
    assert python_functions_signatures(TEST_CODE_WITH_NESTED_FUNCTION) == ['(n)', '(i)']
    assert python_functions_signatures(TEST_CODE_WITH_NESTED_FUNCTION, ignore_nested_functions=True) == ['(n)']


def test_python_traceback_prettify_docs_1():
    traceback = '''File "/app/.heroku/python/lib/python3.6/site-packages/django/core/handlers/exception.py", line 41, in inner response = get_response(request) File "/app/.heroku/python/lib/python3.6/site-packages/django/core/handlers/base.py", line 187, in _get_response response = self.process_exception_by_middleware(e, request) File "/app/.heroku/python/lib/python3.6/site-packages/django/core/handlers/base.py", line 185, in _get_response response = wrapped_callback(request, *callback_args, **callback_kwargs)'''
    pretty_traceback = python_traceback_prettify(traceback)
    print('pretty_traceback {}'.format(pretty_traceback))
    assert (
        pretty_traceback
        == '''File "/app/.heroku/python/lib/python3.6/site-packages/django/core/handlers/exception.py", line 41, in inner response = get_response(request)
File "/app/.heroku/python/lib/python3.6/site-packages/django/core/handlers/base.py", line 187, in _get_response response = self.process_exception_by_middleware(e, request)
File "/app/.heroku/python/lib/python3.6/site-packages/django/core/handlers/base.py", line 185, in _get_response response = wrapped_callback(request, *callback_args, **callback_kwargs)'''
    )


def test_python_traceback_pretty_print_docs_1(capsys):
    traceback = '''File "/app/.heroku/python/lib/python3.6/site-packages/django/core/handlers/exception.py", line 41, in inner response = get_response(request) File "/app/.heroku/python/lib/python3.6/site-packages/django/core/handlers/base.py", line 187, in _get_response response = self.process_exception_by_middleware(e, request) File "/app/.heroku/python/lib/python3.6/site-packages/django/core/handlers/base.py", line 185, in _get_response response = wrapped_callback(request, *callback_args, **callback_kwargs)'''
    pretty_traceback = python_traceback_prettify(traceback)
    python_traceback_pretty_print(traceback)
    captured = capsys.readouterr()
    assert captured.out.strip() == pretty_traceback.strip()


def test_python_fstrings_docs_1():
    python_f_strings = tuple(python_fstrings('Hello, {name}. You are {age}.'))
    assert python_f_strings == ('name', 'age')

    python_f_strings = tuple(python_fstrings('Hello, {name}. You are {age}.', include_braces=True))
    assert python_f_strings == ('{name}', '{age}')

    python_f_strings = tuple(python_fstrings('Hello, {new_comedian!r}'))
    assert python_f_strings == ('new_comedian!r',)

    python_f_strings = tuple(python_fstrings('Hello, {}'.format('Bob')))
    assert python_f_strings == ()


def test_python_object_type_to_word_docs_1():
    assert python_object_type_to_word(1) == 'int'
    assert python_object_type_to_word('foo') == 'str'
    assert python_object_type_to_word([]) == 'list'
    assert python_object_type_to_word({}) == 'dict'
    assert python_object_type_to_word({1, 2, 3}) == 'set'
    assert python_object_type_to_word(('foo', 'bar')) == 'tuple'
    assert python_object_type_to_word(True) == 'bool'
    assert python_object_type_to_word(2.0) == 'float'

    class Animal:
        pass

    a = Animal()
    assert python_object_type_to_word(a) == 'Animal'


def test_python_make_pythonic_docs_1():
    assert python_make_pythonic('fooBar') == 'foo_bar'
    assert python_make_pythonic('foo-bar') == 'foo_bar'
    assert python_make_pythonic('foo bar') == 'foo_bar'
    assert python_make_pythonic('Foo Bar') == 'foo_bar'
    # make sure that consecutive capital letters are not split up
    assert python_make_pythonic('ET Phone Home') == 'et_phone_home'
    assert python_make_pythonic('IP address data') == 'ip_address_data'


def test_python_object_source_file_docs_1():
    result = python_object_source_file(file_read)
    assert result.endswith('d8s_file_system/files.py')


def test_python_object_module_docs_1():
    result = python_object_module(file_read)
    assert result == 'd8s_file_system.files'


def test_python_sort_type_list_by_name_docs_1():
    result = python_sort_type_list_by_name([str, int, tuple, float])
    assert result == [float, int, str, tuple]

    result = python_sort_type_list_by_name([str, int, tuple, float], reverse=True)
    assert result == [tuple, str, int, float]


def test_python_file_names_docs_1():
    # TODO: create a directory of data locally that we test against
    assert python_file_names(TEST_DIRECTORY_PATH) == ['a.py', 'a_test.py']
    assert python_file_names(TEST_DIRECTORY_PATH, exclude_tests=True) == ['a.py']


def test_python_files_using_function_docs_1():
    results = python_files_using_function('python_files_using_function', os.path.dirname(__file__))
    LOCAL_DOCKER_PATH = '/code/tests/test_python_data.py'
    GITHUB_ACTIONS_PATH = '/home/runner/work/d8s-python/d8s-python/tests/test_python_data.py'
    assert results == [LOCAL_DOCKER_PATH] or [GITHUB_ACTIONS_PATH]


def test_python_is_version_2_docs_1():
    assert not python_is_version_2()


def test_python_is_version_3_docs_1():
    assert python_is_version_3()


def test_python_keywords_docs_1():
    assert isinstance(python_keywords(), list)
    assert 30 < len(python_keywords()) < 40
    # assert python_keywords(code_text=SIMPLE_FUNCTION) == ['def', 'return']


def test_python_object_properties_enumerate_docs__no_properties():
    assert python_object_properties_enumerate('foo') is None


def test_python_function_blocks_1():
    result = python_function_blocks(SIMPLE_FUNCTION)
    assert result == ['def test(a) -> List:\n    print(a)\n\n    return []']

    s = '''def a(
    n: str, o: Callable
):
    print('foo')'''
    assert python_function_blocks(s) == [s]

    s = '''def a(
    n: str, o: Callable
):
    print("""in the beginning
was the word
and the word...""")
    x = 10
    if x == 1:
        x = 1
    elif x == 2:
        x = 2
    else:
      print('bar')


a = 1
b = 2
c = 3
myList = range(10)

def someMethod(x):
    something = x * 2
    def subfunction(something):
        print('here')
    return something

f = someMethod(b)

print(f)'''
    assert python_function_blocks(s) == [
        'def a(\n    n: str, o: Callable\n):\n    print("""in the beginning\nwas the word\nand the word...""")\n    x = 10\n    if x == 1:\n        x = 1\n    elif x == 2:\n        x = 2\n    else:\n      print(\'bar\')',
        "def someMethod(x):\n    something = x * 2\n    def subfunction(something):\n        print('here')\n    return something",
        "    def subfunction(something):\n        print('here')",
    ]

    s = '''@do.something
def _a(
    n: str, o: Callable
):
    print('foo')'''
    assert python_function_blocks(s) == [s]
    assert python_function_blocks(s, ignore_private_functions=True) == []


def test_python_function_blocks__ignore_nested_function():
    assert python_function_blocks(TEST_CODE_WITH_NESTED_FUNCTION) == [
        'def f(n):\n    """a."""\n    def sq(i):\n        """b."""\n        return i * i\n    return sq(n)',
        '    def sq(i):\n        """b."""\n        return i * i',
    ]
    assert python_function_blocks(TEST_CODE_WITH_NESTED_FUNCTION, ignore_nested_functions=True) == [
        'def f(n):\n    """a."""\n    def sq(i):\n        """b."""\n        return i * i\n    return sq(n)'
    ]


def test_python_function_blocks_edge_cases_1():
    # when this tests was written, the python_function_blocks function wasn't finding anything after "b(\n        1"
    s = '''def a():
    def b(n):
        return (
            n * 2
        )

    return b(
        1
    )'''
    assert python_function_blocks(s) == [
        'def a():\n    def b(n):\n        return (\n            n * 2\n        )\n\n    return b(\n        1\n    )',
        '    def b(n):\n        return (\n            n * 2\n        )',
    ]

    s = '''def a():
    return some_collection.get_objects(locator=l5) \
                      .get_distinct(case_insensitive=True) \
                      .filter(predicate=query(q5)) \
                      .values()'''
    assert python_function_blocks(s) == [
        'def a():\n    return some_collection.get_objects(locator=l5)                       .get_distinct(case_insensitive=True)                       .filter(predicate=query(q5))                       .values()'
    ]

    s = '''def a():
    return "foo" +\
    "bar"'''
    print(f'python_function_blocks(s): {python_function_blocks(s)}')
    assert python_function_blocks(s) == ['def a():\n    return "foo" +    "bar"']


def test_python_function_blocks__async_functions():
    assert python_function_blocks(TEST_CODE_WITH_ASYNC_FUNCTION) == [
        'def foo(n):\n    """Foo."""\n    return n',
        'async def bar(n):\n    """Some async func."""\n    return n',
    ]
