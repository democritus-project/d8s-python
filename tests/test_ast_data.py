import ast

from d8s_python import (
    python_ast_exception_handler_exceptions_raised,
    python_ast_function_defs,
    python_ast_object_line_numbers,
    python_ast_objects_not_of_type,
    python_ast_objects_of_type,
    python_ast_parse,
    python_constants,
    python_exceptions_handled,
    python_exceptions_raised,
    python_function_argument_annotations,
    python_function_argument_defaults,
    python_function_argument_names,
    python_function_arguments,
    python_function_docstrings,
    python_function_names,
    python_functions_as_import_string,
    python_variable_names,
)
from d8s_python.ast_data import _python_ast_clean

TEST_CODE = '''

async def foo():
    """."""
    print('Here!')


def python_function_names(code_text: str, *, ignore_private_functions: bool = False) -> List[str]:
    """."""
    function_objects = python_ast_function_defs(code_text)
    function_names = [f.name for f in function_objects]
    if ignore_private_functions:
        function_names = [name for name in function_names if not name.startswith('_')]
    return function_names


# TODO: write functions to get docstrings for classes and modules
def python_function_docstrings(code_text: str, *, ignore_private_functions: bool = False) -> List[str]:
    """Get docstrings for all of the functions in the given text."""
    function_objects = python_ast_function_defs(code_text)
    docstrings = [
        ast.get_docstring(f) for f in function_objects if not (ignore_private_functions and f.name.startswith('_'))
    ]
    return docstrings


def python_variable_names(code_text: str) -> List[str]:
    """Get all of the variables names in the code_text."""
    # TODO: add a caveat that this function will only find *stored* variables and not those which are referenced or loaded. E.g., given "x = y + 1", this function will return ["x"]; note that "y" is not included
    parsed_code = python_ast_parse(code_text)
    variable_names = [
        node.id for node in ast.walk(parsed_code) if isinstance(node, ast.Name) and (isinstance(node.ctx, ast.Store))
    ]
    return variable_names


def python_constants(code_text: str) -> List[str]:
    """Get all constants in the code_text."""
    # TODO: add a caveat that this function will only find *stored* variables which are uppercased
    variables = python_variable_names(code_text)
    constants = [var for var in variables if var.isupper()]
    return constants

'''

TEST_CODE_1 = '''a = 1
b = 2
c = 3
myList = range(10)

def someMethod(x):
    something = x * 2
    return something

f = someMethod(b)

print(f)'''

TEST_CODE_WITH_EXCEPTION = '''try:
    return a  / b
except ZeroDivisionError:
    raise'''

TEST_CODE_WITH_PRIVATE_FUNCTION = '''def _test(a: str):
    """Docstring."""
    return a'''

TEST_FUNCTION_WITH_DEFAULT = '''def test(a: str = ''):
    """Docstring."""
    return a'''

TEST_CODE_WITH_NESTED_FUNCTION = '''
def f(n):
    """a."""
    def sq(i):
        """b."""
        return i * i
    return sq(n)
'''

TEST_CODE_WITH_ASYNC_FUNCTION = '''
def foo(n):
    """Foo."""
    return n


async def bar(n):
    """Some async func."""
    return n
'''

TEST_EXCEPTION_DATA = [
    {  # test a simple raise
        'code': '''raise ValueError('I cannot divide by zero')''',
        'handled': [],
        'raised': ['ValueError'],
    },
    {  # test a simple raise (in a context)
        'code': '''if d == 0:
    raise ValueError('I cannot divide by zero')
else:
    return n / d''',
        'handled': [],
        'raised': ['ValueError'],
    },
    {  # test code where an error that is part of another module is raised
        'code': '''raise pint.UndefinedUnitError('"Foo" is not a valid unit')''',
        'handled': [],
        'raised': ['pint.UndefinedUnitError'],
    },
    {  # ('one', ('afore_mentioned', ('custom', 'explicit')))
        'code': '''try:\n\tpass\nexcept pint.UndefinedUnitError:\n\traise pint.UndefinedUnitError('"Foo" is not a valid unit')''',
        'handled': ['pint.UndefinedUnitError'],
        'raised': ['pint.UndefinedUnitError'],
    },
    {  # ('one', ('afore_mentioned', ('custom', 'named_before_except')))
        'code': '''e = pint.UndefinedUnitError('"Foo" is not a valid unit')\ntry:\n\tpass\nexcept e:\n\traise e''',
        'handled': ['e'],
        'raised': ['e'],
    },
    {  # ('one', ('afore_mentioned', ('custom', 'named_in_except')))
        'code': '''try:\n\tpass\nexcept pint.UndefinedUnitError as e:\n\traise e''',
        'handled': ['pint.UndefinedUnitError'],
        'raised': ['pint.UndefinedUnitError'],
    },
    {  # ('one', ('afore_mentioned', ('built_in', 'explicit')))
        'code': '''try:\n\tpass\nexcept RuntimeError:\n\traise RuntimeError('"Foo" is not a valid unit')''',
        'handled': ['RuntimeError'],
        'raised': ['RuntimeError'],
    },
    {  # ('one', ('afore_mentioned', ('built_in', 'named_before_except')))
        'code': '''e = ValueError('"Foo" is not a valid unit')\ntry:\n\tpass\nexcept e:\n\traise e''',
        'handled': ['e'],
        'raised': ['e'],
    },
    {  # ('one', ('afore_mentioned', ('built_in', 'named_in_except')))
        'code': '''try:\n\tpass\nexcept RuntimeError as e:\n\traise e''',
        'handled': ['RuntimeError'],
        'raised': ['RuntimeError'],
    },
    {  # ('one', ('different', ('custom', 'explicit')))
        'code': '''try:\n\tpass\nexcept RuntimeError:\n\traise pint.UndefinedUnitError('"Foo" is not a valid unit')''',
        'handled': ['RuntimeError'],
        'raised': ['pint.UndefinedUnitError'],
    },
    {  # ('one', ('different', ('custom', 'named_before_except')))
        'code': '''e = pint.UndefinedUnitError('"Foo" is not a valid unit')\ntry:\n\tpass\nexcept ValueError:\n\traise e''',
        'handled': ['ValueError'],
        'raised': ['e'],
    },
    {  # ('one', ('different', ('built_in', 'explicit')))
        'code': '''try:\n\tpass\nexcept ValueError:\n\traise RuntimeError''',
        'handled': ['ValueError'],
        'raised': ['RuntimeError'],
    },
    {  # ('one', ('different', ('built_in', 'named_before_except')))
        'code': '''e = ValueError\ntry:\n\tpass\nexcept RuntimeError:\n\traise e''',
        'handled': ['RuntimeError'],
        'raised': ['e'],
    },
    {  # ('one', '') - with built-in exception
        'code': '''try:\n\tpass\nexcept RuntimeError:\n\traise''',
        'handled': ['RuntimeError'],
        'raised': ['RuntimeError'],
    },
    {  # ('one', '') - with custom exception
        'code': '''try:\n\tpass\nexcept pint.UndefinedUnitError:\n\traise''',
        'handled': ['pint.UndefinedUnitError'],
        'raised': ['pint.UndefinedUnitError'],
    },
    {  # ('many', ('afore_mentioned', ('custom', 'explicit')))
        'code': '''try:\n\tpass\nexcept (pint.UndefinedUnitError, pint.FooBarError):\n\traise pint.UndefinedUnitError('"Foo" is not a valid unit')''',
        'handled': ['pint.UndefinedUnitError', 'pint.FooBarError'],
        'raised': ['pint.UndefinedUnitError'],
    },
    {  # ('many', ('afore_mentioned', ('custom', 'named_before_except')))
        'code': '''e = pint.UndefinedUnitError('"Foo" is not a valid unit')\ntry:\n\tpass\nexcept (e, pint.FooBarError):\n\traise e''',
        'handled': ['e', 'pint.FooBarError'],
        'raised': ['e'],
    },
    {  # ('many', ('afore_mentioned', ('custom', 'named_in_except')))
        'code': '''try:\n\tpass\nexcept (pint.UndefinedUnitError, pint.FooBarError) as e:\n\traise e''',
        'handled': ['pint.UndefinedUnitError', 'pint.FooBarError'],
        'raised': ['pint.UndefinedUnitError', 'pint.FooBarError'],
    },
    {  # ('many', ('afore_mentioned', ('built_in', 'explicit')))
        'code': '''try:\n\tpass\nexcept (RuntimeError, RuntimeWarning):\n\traise RuntimeError('"Foo" is not a valid unit')''',
        'handled': ['RuntimeError', 'RuntimeWarning'],
        'raised': ['RuntimeError'],
    },
    {  # ('many', ('afore_mentioned', ('built_in', 'named_before_except')))
        'code': '''e = ValueError('"Foo" is not a valid unit')\ntry:\n\tpass\nexcept (e, RuntimeError):\n\traise e''',
        'handled': ['e', 'RuntimeError'],
        'raised': ['e'],
    },
    {  # ('many', ('afore_mentioned', ('built_in', 'named_in_except')))
        'code': '''try:\n\tpass\nexcept (RuntimeError, RuntimeWarning) as e:\n\traise e''',
        'handled': ['RuntimeError', 'RuntimeWarning'],
        'raised': ['RuntimeError', 'RuntimeWarning'],
    },
    {  # ('many', ('different', ('custom', 'explicit')))
        'code': '''try:\n\tpass\nexcept (pint.AError, pint.BError):\n\traise pint.UndefinedUnitError('"Foo" is not a valid unit')''',
        'handled': ['pint.AError', 'pint.BError'],
        'raised': ['pint.UndefinedUnitError'],
    },
    {  # ('many', ('different', ('custom', 'named_before_except')))
        'code': '''e = pint.UndefinedUnitError('"Foo" is not a valid unit')\ntry:\n\tpass\nexcept (ValueError, RuntimeError):\n\traise e''',
        'handled': ['ValueError', 'RuntimeError'],
        'raised': ['e'],
    },
    {  # ('many', ('different', ('built_in', 'explicit')))
        'code': '''try:\n\tpass\nexcept (ValueError, AssertionError):\n\traise RuntimeError''',
        'handled': ['ValueError', 'AssertionError'],
        'raised': ['RuntimeError'],
    },
    {  # ('many', ('different', ('built_in', 'named_before_except')))
        'code': '''e = ValueError\ntry:\n\tpass\nexcept (RuntimeError, RuntimeWarning):\n\traise e''',
        'handled': ['RuntimeError', 'RuntimeWarning'],
        'raised': ['e'],
    },
    {  # ('many', '') - with built-in exception
        'code': '''try:\n\tpass\nexcept (RuntimeError, RuntimeWarning):\n\traise''',
        'handled': ['RuntimeError', 'RuntimeWarning'],
        'raised': ['RuntimeError', 'RuntimeWarning'],
    },
    {  # ('many', '') - with custom exception
        'code': '''try:\n\tpass\nexcept (pint.UndefinedUnitError, pint.AError):\n\traise''',
        'handled': ['pint.UndefinedUnitError', 'pint.AError'],
        'raised': ['pint.UndefinedUnitError', 'pint.AError'],
    },
]


def test_python_ast_exception_handler_exceptions_raised_1():
    except_handler = tuple(python_ast_objects_of_type(TEST_CODE_WITH_EXCEPTION, ast.ExceptHandler))[0]
    result = python_ast_exception_handler_exceptions_raised(except_handler)
    assert tuple(result) == ('ZeroDivisionError',)


def test_python_ast_objects_not_of_type_docs_1():
    # make sure that any ast.FunctionDef objects *and* their children are not returned
    result = tuple(python_ast_objects_not_of_type(TEST_CODE_1, ast.FunctionDef))
    assert len(result) == 35


def test_python_ast_objects_of_type_1():
    result = list(python_ast_objects_of_type(TEST_CODE_1, ast.FunctionDef))
    assert len(result) == 1
    assert isinstance(result[0], ast.FunctionDef)


def test_python_ast_objects_of_type__only_first_level():
    # test without limiting search to the first level
    assert len(tuple(python_ast_objects_of_type(TEST_CODE_WITH_NESTED_FUNCTION, ast.FunctionDef))) == 2

    # test limiting search to the first level
    result = tuple(python_ast_objects_of_type(TEST_CODE_WITH_NESTED_FUNCTION, ast.FunctionDef, recursive_search=False))
    assert len(result) == 1
    assert isinstance(result[0], ast.FunctionDef)


def test_python_exceptions_handled_docs_1():
    for test in TEST_EXCEPTION_DATA:
        try:
            assert list(python_exceptions_handled(test['code'])) == test['handled']
        except AssertionError as e:
            failure = (test, e)
            print(failure)
            raise e


def test_python_ast_object_line_numbers_docs_1():
    result = python_ast_object_line_numbers(python_ast_parse(TEST_CODE_WITH_PRIVATE_FUNCTION))
    assert result == (1, 3)

    result = python_ast_object_line_numbers(python_ast_parse(TEST_FUNCTION_WITH_DEFAULT))
    assert result == (1, 3)

    s = '''def democritus_directory_documentation_create(directory_path: str, *, track_changes: bool = True):
    """Create documentation files for all non-test python files in the given directory_path."""
    _directory_documentation_action(
        directory_path, democritus_functions_file_documentation_create, track_changes=track_changes
    )'''
    result = python_ast_object_line_numbers(python_ast_parse(s))
    assert result == (1, 4)


def test_python_exceptions_raised_docs_1():
    for test in TEST_EXCEPTION_DATA:
        try:
            assert list(python_exceptions_raised(test['code'])) == test['raised']
        except AssertionError as e:
            failure = (test, e)
            print(failure)
            raise e


def test_python_functions_as_import_string_1():
    assert (
        python_functions_as_import_string(TEST_CODE, 'ast_data')
        == 'from ast_data import (\n    python_function_names,\n    python_function_docstrings,\n    python_variable_names,\n    python_constants,\n    foo,\n)'
    )


def test__python_ast_clean_1():
    assert _python_ast_clean('print("foo\nbar")') == 'print("foo\\nbar")'


def test_python_ast_parse_1():
    result = python_ast_parse(TEST_CODE_1)
    assert isinstance(result, ast.Module)


def test_python_ast_parse__code_has_newlines():
    code_string = '''print("foo")\nprint("bar")'''
    result = python_ast_parse(code_string)
    assert isinstance(result, ast.Module)


def test_python_ast_function_defs_1():
    result = tuple(python_ast_function_defs(TEST_FUNCTION_WITH_DEFAULT))
    assert len(result) == 1
    assert isinstance(result[0], ast.FunctionDef)

    result = tuple(python_ast_function_defs(TEST_CODE_WITH_PRIVATE_FUNCTION))
    assert len(result) == 1
    assert isinstance(result[0], ast.FunctionDef)


def test_python_function_arguments_1():
    result = python_function_arguments(TEST_FUNCTION_WITH_DEFAULT)
    assert len(result) == 1
    assert isinstance(result[0], ast.arg)


def test_python_function_argument_names_1():
    assert tuple(python_function_argument_names(TEST_FUNCTION_WITH_DEFAULT)) == ('a',)


def test_python_function_argument_defaults_1():
    result = python_function_argument_defaults(TEST_FUNCTION_WITH_DEFAULT)
    assert len(result) == 1
    assert isinstance(result[0], ast.Str)

    result = python_function_argument_defaults(TEST_CODE_WITH_PRIVATE_FUNCTION)
    assert len(result) == 0


def test_python_function_argument_annotations_1():
    assert (
        list(
            python_function_argument_annotations(
                '''def _test(a: str):
    """Docstring."""
    return a'''
            )
        )
        == ['str']
    )
    assert (
        list(
            python_function_argument_annotations(
                '''def _test(a):
    """Docstring."""
    return a'''
            )
        )
        == [None]
    )


def test_python_function_names_1():
    assert python_function_names(TEST_CODE) == [
        'python_function_names',
        'python_function_docstrings',
        'python_variable_names',
        'python_constants',
        'foo',
    ]
    assert python_function_names(TEST_CODE_WITH_PRIVATE_FUNCTION) == ['_test']
    assert python_function_names(TEST_CODE_WITH_PRIVATE_FUNCTION, ignore_private_functions=True) == []


def test_python_function_names__nested_functions():
    assert python_function_names(TEST_CODE_WITH_NESTED_FUNCTION) == ['f', 'sq']
    assert python_function_names(TEST_CODE_WITH_NESTED_FUNCTION, ignore_nested_functions=True) == ['f']


def test_python_function_names__async_functions():
    assert python_function_names(TEST_CODE_WITH_ASYNC_FUNCTION) == ['foo', 'bar']


def test_python_function_docstrings_1():
    code_text = '''def _test(a: str):
    """Docstring."""
    return a'''
    assert python_function_docstrings(code_text) == ['Docstring.']
    assert python_function_docstrings(code_text, ignore_private_functions=True) == []


def test_python_function_docstrings__nested_functions():
    assert python_function_docstrings(TEST_CODE_WITH_NESTED_FUNCTION) == ['a.', 'b.']
    assert python_function_docstrings(TEST_CODE_WITH_NESTED_FUNCTION, ignore_nested_functions=True) == ['a.']


def test_python_function_docstrings__async_functions():
    assert python_function_docstrings(TEST_CODE_WITH_ASYNC_FUNCTION) == ['Foo.', 'Some async func.']


def test_python_variable_names_1():
    assert python_variable_names('x = 7') == ['x']
    assert python_variable_names('x = y + 7') == ['x']
    assert python_variable_names('PI = 3.14') == ['PI']
    assert python_variable_names('1 + 0') == []
    assert python_variable_names(TEST_CODE_1) == ['a', 'b', 'c', 'myList', 'f', 'something']


def test_python_constants_1():
    assert python_constants('x = 7') == []
    assert python_constants('PI = 3.14') == ['PI']
    assert python_constants('1 + 0') == []
