import argparse
import re
import sys
from typing import Any, Iterator, List, Union


# @decorators.map_firstp_arg
def python_functions_signatures(
    code_text: str,
    *,
    ignore_private_functions: bool = False,
    ignore_nested_functions: bool = False,
    keep_function_name: bool = False,
) -> List[str]:
    """Return the function signatures for all of the functions in the given code_text."""
    from d8s_strings import string_remove_from_start

    from .ast_data import python_function_names

    signatures = []

    function_names = python_function_names(
        code_text, ignore_private_functions=ignore_private_functions, ignore_nested_functions=ignore_nested_functions
    )

    for name in function_names:
        regex_for_signature = fr'(def {name}\((?:.|\s)*?\).*?):'
        sig = re.findall(regex_for_signature, code_text)
        if any(sig):
            new_sig = string_remove_from_start(sig[0], 'def ')
            if not keep_function_name:
                new_sig = string_remove_from_start(new_sig, name)
            signatures.append(new_sig)
        else:
            message = f'Unable to find signature for the {name} function'
            print(message)
            signatures.append(None)

    return signatures


def python_todos(code_text: str, todo_regex: str = 'TODO:.*') -> List[str]:
    """Return all todos in the given code_text that match the given todo_regex."""
    todos = re.findall(todo_regex, code_text)
    return todos


# @decorators.map_first_arg
def python_make_pythonic(name: str) -> str:
    """Make the name pythonic.

    (e.g. 'fooBar' => 'foo_bar', 'foo-bar' => 'foo_bar', 'foo bar' => 'foo_bar', 'Foo Bar' => 'foo_bar').
    """
    from d8s_strings import lowercase, snake_case, string_split_on_uppercase

    split_string = '_'.join(
        [
            string.strip()
            for string in string_split_on_uppercase(name, include_uppercase_characters=True, split_acronyms=False)
        ]
    )
    split_string = lowercase(split_string)
    result = snake_case(split_string)
    return result


# @decorators.map_first_arg
def python_namespace_has_argument(namespace: argparse.Namespace, argument_name: str) -> bool:
    """."""
    result = argument_name in namespace
    return result


# @decorators.map_first_arg
def python_traceback_prettify(traceback: str) -> str:
    """Return a string with the given traceback pretty-printed."""
    pretty_traceback = re.sub(' File ', '\nFile ', traceback)

    return pretty_traceback


# @decorators.map_first_arg
def python_traceback_pretty_print(traceback: str) -> None:
    """Return a string with the given traceback pretty-printed."""
    prettified_string = python_traceback_prettify(traceback)
    print(prettified_string)


# @decorators.map_first_arg
def python_clean(code_text: str) -> str:
    """Clean python code as it is often found in documentation and snippets."""
    code_text = code_text.replace('>>> ', '')
    code_text = code_text.replace('... ', '')
    return code_text


def python_function_blocks(
    code_text: str, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False
) -> List[str]:
    """Find the code (as a string) for every function in the given code_text."""
    from d8s_lists import has_index
    from d8s_strings import string_chars_at_start_len

    from .ast_data import python_ast_function_defs, python_ast_object_line_numbers

    function_block_strings = []
    code_text_as_lines = code_text.splitlines()
    ast_function_defs = python_ast_function_defs(code_text, recursive_search=not ignore_nested_functions)
    function_block_line_numbers = [(f.name, python_ast_object_line_numbers(f)) for f in ast_function_defs]

    for function_name, (start, end) in function_block_line_numbers:
        function_block_lines = code_text_as_lines[start - 1 : end]  # noqa=E203
        function_block_string = '\n'.join(function_block_lines)

        if ignore_private_functions:
            if function_name.startswith('_'):
                continue

        # the code below checks to see if the line after what was determined to be the last line of the function...
        # should also be included in the function block (which is the case when the closing parenthesis of a...
        # function call in another function is on a newline (see the...
        # python_data_tests.py::test_python_function_blocks_edge_cases_1 for an example))
        if has_index(code_text_as_lines, end):
            # find the indentation level of the function definition (the first line of the function)
            function_indentation = string_chars_at_start_len(function_block_lines[0], ' ')
            # TODO: the check below assumes that spaces are used instead of tabs
            next_line_is_indented = (
                code_text_as_lines[end].startswith(' ')
                and string_chars_at_start_len(code_text_as_lines[end], ' ') > function_indentation
            )
            next_line_has_only_parenthesis = code_text_as_lines[end].strip(' ') == ')'
            if next_line_is_indented and next_line_has_only_parenthesis:
                function_block_string += f'\n{code_text_as_lines[end]}'
        function_block_strings.append(function_block_string)
    return function_block_strings


def python_line_count(python_code: str, *, ignore_empty_lines: bool = True) -> int:
    """Return the number of lines in the given function_text."""
    from d8s_lists import truthy_items

    lines = python_code.splitlines()
    if ignore_empty_lines:
        return len(tuple(truthy_items(lines)))
    else:
        return len(lines)


def python_function_lengths(code_text: str) -> List[int]:
    """Find the lengths of each function in the given code_text."""
    function_blocks = python_function_blocks(code_text)
    return [python_line_count(function_block) for function_block in function_blocks]


def python_version() -> str:
    """Return the python version of the current environment."""
    return '{}.{}.{}'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)


def python_is_version_2() -> bool:
    """Return whether or not the python version of the current environment is v2.x."""
    return python_version().startswith('2.')


def python_is_version_3() -> bool:
    """Return whether or not the python version of the current environment is v3.x."""
    return not python_is_version_2()


# TODO: need to standardize the order of arguments between functions like this an the directorySearch function
# @decorators.map_first_arg
def python_files_using_function(function_name: str, search_path: str) -> List[str]:
    """Find where the given function is used in the given search path."""
    from d8s_file_system import directory_read_files_with_path_matching

    files_using_function = []

    function_pattern = f'{function_name}('
    python_files = directory_read_files_with_path_matching(search_path, '*.py')
    for file_path, file_contents in python_files:
        if function_pattern in file_contents:
            files_using_function.append(file_path)

    return files_using_function


def python_keywords() -> List[str]:
    """Get a list of the python keywords."""
    import keyword

    return keyword.kwlist

    # if code_text is None:
    #     return python_keywords
    # else:
    #     from d8s_strings import string_words

    #     words_in_code_text = string_words(code_text)
    #     keywords_used = []

    #     for palabra in words_in_code_text:
    #         if palabra in python_keywords:
    #             keywords_used.append(palabra)

    # return keywords_used


# @decorators.map_first_arg
def python_object_properties_enumerate(
    python_object: Any, *, run_methods: bool = True, internal_properties: bool = True
) -> None:
    """Enumerate and print out the properties of the given object."""
    for i in python_object.__dir__():
        if not internal_properties:
            if i.startswith('_'):
                continue

        string_to_eval_as_property = 'python_object.{}'.format(i)
        try:
            if run_methods:
                eval_result = eval(string_to_eval_as_property)  # pylint: disable=W0123
                if callable(eval_result):
                    string_to_eval_as_function = 'python_object.{}()'.format(i)
                    try:
                        print(f'{i}: {eval(string_to_eval_as_function)}')  # pylint: disable=W0123
                    except TypeError:
                        print(f'{i}: {eval(string_to_eval_as_property)}')  # pylint: disable=W0123
                else:
                    print(f'{i}: {eval_result}')
            else:
                print(f'{i}: {eval(string_to_eval_as_property)}')  # pylint: disable=W0123
        except AttributeError:
            print(f'! Unable to get the {i} attribute for the item.')


def python_copy_deep(python_object: Any) -> Any:
    """Return a deep (complete, recursive) copy of the given python object."""
    import copy

    return copy.deepcopy(python_object)


def python_copy_shallow(python_object: Any) -> Any:
    """Return shallow copy of the given python object."""
    import copy

    return copy.copy(python_object)


# @decorators.map_first_arg
def python_file_names(path: str, *, exclude_tests: bool = False) -> List[str]:
    """Find all python files in the given directory."""
    from d8s_file_system import directory_file_names_matching

    files = directory_file_names_matching(path, '*.py')

    if not exclude_tests:
        return files
    else:
        non_test_files = []

        for file in files:
            if '_test' not in file and 'test_' not in file:
                non_test_files.append(file)

        return non_test_files


# @decorators.map_first_arg
def python_fstrings(code_text: str, *, include_braces: bool = False) -> Iterator[str]:
    """Find all of the python formatted string literals in the given text.

    See https://realpython.com/python-f-strings/ for more details about f-strings.
    """
    from d8s_grammars import python_formatted_string_literal
    from d8s_lists import flatten

    python_f_strings = flatten(python_formatted_string_literal.searchString(code_text).asList())

    if not include_braces:
        python_f_strings = (f_string.strip('{').strip('}') for f_string in python_f_strings)

    return python_f_strings


# @decorators.map_first_arg
def python_code_details(code_text: str):
    """Get details about the given code_text. This is a wrapper for `dis.code_info`"""
    import dis

    return dis.code_info(code_text)


# @decorators.map_first_arg
def python_disassemble(code_text: str):
    """Disassemble the python code_text. This is a wrapper for `dis.dis`"""
    import dis

    return dis.Bytecode(code_text).dis()


def python_stack_local_data():
    """Get local data in the current python environment."""
    import inspect

    return inspect.currentframe().f_locals


# @decorators.map_first_arg
def python_object_doc_string(python_object: Any) -> Union[str, None]:
    """Get the doc string for the given python object (e.g. module, function, or class)."""
    import inspect

    return inspect.getdoc(python_object)


# @decorators.map_first_arg
def python_object_source_file(python_object: Any) -> str:
    """Get the source file for the given python object (e.g. module, function, or class)."""
    import inspect

    return inspect.getsourcefile(python_object)


# @decorators.map_first_arg
def python_object_module(python_object: Any) -> str:
    """Get the module for the given python object (e.g. function or class)."""
    return python_object.__module__


# @decorators.map_first_arg
def python_object_source_code(python_object: Any) -> str:
    """Get the source code for the given python object (e.g. module, function, or class)."""
    import inspect

    return inspect.getsource(python_object)


# @decorators.map_first_arg
def python_object_signature(python_object: Any) -> str:
    """Get the argument signature for the given python object (e.g. module, function, or class)."""
    import inspect

    return inspect.signature(python_object)


# TODO: improve the type annotations to be lists of types
def python_sort_type_list_by_name(python_type_list: List[type], **kwargs) -> List[type]:
    """."""
    return sorted(python_type_list, key=lambda x: python_type_name(x), **kwargs)  # pylint: disable=W0108


# @decorators.map_first_arg
def python_type_name(python_type: type) -> str:
    """Return the common name of the given type."""
    return python_type.__name__


def python_object_type_to_word(python_object: Any) -> str:
    """Convert the given python type to a string."""
    return python_type_name(type(python_object))
