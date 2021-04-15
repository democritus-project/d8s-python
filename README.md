# Democritus Python

[![PyPI](https://img.shields.io/pypi/v/d8s-python.svg)](https://pypi.python.org/pypi/d8s-python)
[![CI](https://github.com/democritus-project/d8s-python/workflows/CI/badge.svg)](https://github.com/democritus-project/d8s-python/actions)
[![Lint](https://github.com/democritus-project/d8s-python/workflows/Lint/badge.svg)](https://github.com/democritus-project/d8s-python/actions)
[![codecov](https://codecov.io/gh/democritus-project/d8s-python/branch/main/graph/badge.svg?token=V0WOIXRGMM)](https://codecov.io/gh/democritus-project/d8s-python)
[![The Democritus Project uses semver version 2.0.0](https://img.shields.io/badge/-semver%20v2.0.0-22bfda)](https://semver.org/spec/v2.0.0.html)
[![The Democritus Project uses black to format code](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://choosealicense.com/licenses/lgpl-3.0/)

Democritus functions<sup>[1]</sup> for working with Python data (code and ASTs).

[1] Democritus functions are <i>simple, effective, modular, well-tested, and well-documented</i> Python functions.

We use `d8s` as an abbreviation for `democritus` (you can read more about this [here](https://github.com/democritus-project/roadmap#what-is-d8s)).

## Functions

  - ```python
    def python_functions_signatures(
        code_text: str,
        *,
        ignore_private_functions: bool = False,
        ignore_nested_functions: bool = False,
        keep_function_name: bool = False,
    ) -> List[str]:
        """Return the function signatures for all of the functions in the given code_text."""
    ```
  - ```python
    def python_todos(code_text: str, todo_regex: str = 'TODO:.*') -> List[str]:
        """Return all todos in the given code_text that match the given todo_regex."""
    ```
  - ```python
    def python_make_pythonic(name: str) -> str:
        """Make the name pythonic.
    
    (e.g. 'fooBar' => 'foo_bar', 'foo-bar' => 'foo_bar', 'foo bar' => 'foo_bar', 'Foo Bar' => 'foo_bar')."""
    ```
  - ```python
    def python_namespace_has_argument(namespace: argparse.Namespace, argument_name: str) -> bool:
        """."""
    ```
  - ```python
    def python_traceback_prettify(traceback: str) -> str:
        """Return a string with the given traceback pretty-printed."""
    ```
  - ```python
    def python_traceback_pretty_print(traceback: str) -> None:
        """Return a string with the given traceback pretty-printed."""
    ```
  - ```python
    def python_clean(code_text: str) -> str:
        """Clean python code as it is often found in documentation and snippets."""
    ```
  - ```python
    def python_function_blocks(
        code_text: str, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False
    ) -> List[str]:
        """Find the code (as a string) for every function in the given code_text."""
    ```
  - ```python
    def python_line_count(python_code: str, *, ignore_empty_lines: bool = True) -> int:
        """Return the number of lines in the given function_text."""
    ```
  - ```python
    def python_function_lengths(code_text: str) -> List[int]:
        """Find the lengths of each function in the given code_text."""
    ```
  - ```python
    def python_version() -> str:
        """Return the python version of the current environment."""
    ```
  - ```python
    def python_is_version_2() -> bool:
        """Return whether or not the python version of the current environment is v2.x."""
    ```
  - ```python
    def python_is_version_3() -> bool:
        """Return whether or not the python version of the current environment is v3.x."""
    ```
  - ```python
    def python_files_using_function(function_name: str, search_path: str) -> List[str]:
        """Find where the given function is used in the given search path."""
    ```
  - ```python
    def python_keywords() -> List[str]:
        """Get a list of the python keywords."""
    ```
  - ```python
    def python_object_properties_enumerate(
        python_object: Any, *, run_methods: bool = True, internal_properties: bool = True
    ) -> None:
        """Enumerate and print out the properties of the given object."""
    ```
  - ```python
    def python_copy_deep(python_object: Any) -> Any:
        """Return a deep (complete, recursive) copy of the given python object."""
    ```
  - ```python
    def python_copy_shallow(python_object: Any) -> Any:
        """Return shallow copy of the given python object."""
    ```
  - ```python
    def python_file_names(path: str, *, exclude_tests: bool = False) -> List[str]:
        """Find all python files in the given directory."""
    ```
  - ```python
    def python_fstrings(code_text: str, *, include_braces: bool = False) -> Iterator[str]:
        """Find all of the python formatted string literals in the given text. See https://realpython.com/python-f-strings/ for more details about f-strings."""
    ```
  - ```python
    def python_code_details(code_text: str):
        """Get details about the given code_text. This is a wrapper for `dis.code_info`"""
    ```
  - ```python
    def python_disassemble(code_text: str):
        """Disassemble the python code_text. This is a wrapper for `dis.dis`"""
    ```
  - ```python
    def python_stack_local_data():
        """Get local data in the current python environment."""
    ```
  - ```python
    def python_object_doc_string(python_object: Any) -> Union[str, None]:
        """Get the doc string for the given python object (e.g. module, function, or class)."""
    ```
  - ```python
    def python_object_source_file(python_object: Any) -> str:
        """Get the source file for the given python object (e.g. module, function, or class)."""
    ```
  - ```python
    def python_object_module(python_object: Any) -> str:
        """Get the module for the given python object (e.g. function or class)."""
    ```
  - ```python
    def python_object_source_code(python_object: Any) -> str:
        """Get the source code for the given python object (e.g. module, function, or class)."""
    ```
  - ```python
    def python_object_signature(python_object: Any) -> str:
        """Get the argument signature for the given python object (e.g. module, function, or class)."""
    ```
  - ```python
    def python_sort_type_list_by_name(python_type_list: List[type], **kwargs) -> List[type]:
        """."""
    ```
  - ```python
    def python_type_name(python_type: type) -> str:
        """Return the common name of the given type."""
    ```
  - ```python
    def python_object_type_to_word(python_object: Any) -> str:
        """Convert the given python type to a string."""
    ```
  - ```python
    def python_ast_raise_name(node: ast.Raise) -> Optional[str]:
        """Get the name of the exception raise by the given ast.Raise object."""
    ```
  - ```python
    def python_ast_exception_handler_exceptions_handled(handler: ast.ExceptHandler) -> Optional[Iterable[str]]:
        """Return all of the exceptions handled by the given exception handler."""
    ```
  - ```python
    def python_ast_exception_handler_exceptions_raised(handler: ast.ExceptHandler) -> Optional[Iterable[str]]:
        """Return the exception raised by the given exception handler."""
    ```
  - ```python
    def python_exceptions_handled(code_text: str) -> Iterable[str]:
        """Return a list of all exceptions handled in the given code."""
    ```
  - ```python
    def python_exceptions_raised(code_text: str) -> Iterable[str]:
        """Return a list of all exceptions raised in the given code."""
    ```
  - ```python
    def python_functions_as_import_string(code_text: str, module_name: str) -> str:
        """."""
    ```
  - ```python
    def python_ast_object_line_number(ast_object: object) -> Optional[int]:
        """."""
    ```
  - ```python
    def python_ast_object_line_numbers(ast_object: object) -> Tuple[int, int]:
        """."""
    ```
  - ```python
    def python_ast_objects_of_type(
        code_text_or_ast_object: Union[str, object], ast_type: type, *, recursive_search: bool = True
    ) -> Iterable[object]:
        """Return all of the ast objects of the given ast_type in the code_text_or_ast_object."""
    ```
  - ```python
    def python_ast_objects_not_of_type(code_text_or_ast_object: Union[str, object], ast_type: type) -> Iterable[object]:
        """Return all of the ast objects which are not of the given ast_type in the code_text_or_ast_object."""
    ```
  - ```python
    def python_ast_parse(code_text: str) -> ast.Module:
        """."""
    ```
  - ```python
    def python_ast_function_defs(code_text: str, recursive_search: bool = True) -> Iterable[ast.FunctionDef]:
        """."""
    ```
  - ```python
    def python_function_arguments(function_text: str) -> List[ast.arg]:
        """."""
    ```
  - ```python
    def python_function_argument_names(function_text: str) -> Iterable[str]:
        """."""
    ```
  - ```python
    def python_function_argument_defaults(function_text: str) -> List[str]:
        """."""
    ```
  - ```python
    def python_function_argument_annotations(function_text: str) -> List[str]:
        """."""
    ```
  - ```python
    def python_function_names(
        code_text: str, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False
    ) -> List[str]:
        """."""
    ```
  - ```python
    def python_function_docstrings(
        code_text: str, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False
    ) -> List[str]:
        """Get docstrings for all of the functions in the given text."""
    ```
  - ```python
    def python_variable_names(code_text: str) -> List[str]:
        """Get all of the variables names in the code_text."""
    ```
  - ```python
    def python_constants(code_text: str) -> List[str]:
        """Get all constants in the code_text."""
    ```

## Development

👋 &nbsp;If you want to get involved in this project, we have some short, helpful guides below:

- [contribute to this project 🥇][contributing]
- [test it 🧪][local-dev]
- [lint it 🧹][local-dev]
- [explore it 🔭][local-dev]

If you have any questions or there is anything we did not cover, please raise an issue and we'll be happy to help.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and Floyd Hightower's [Python project template](https://github.com/fhightower-templates/python-project-template).

[contributing]: https://github.com/democritus-project/.github/blob/main/CONTRIBUTING.md#contributing-a-pr-
[local-dev]: https://github.com/democritus-project/.github/blob/main/CONTRIBUTING.md#local-development-
