import argparse
import ast

from typing import Any, Dict, Iterator, List, Union


class python:
    @staticmethod
    def keywords( ) -> List[str]:
        """
        Get a list of the python keywords."""

        import keyword

        return keyword.kwlist


class python_objects:
    def __init__(self, obj: Any): self.object = obj

    def enumerate_properties(self, *, run_methods: bool = True, internal_properties: bool = True) -> None:
        """
        Enumerate and print out the properties of the given object."""

        for i in self.object.__dir__():
            if not internal_properties and i.startswith('_'): continue

            eval_property = f"python_object.{i}"
            try:
                if run_methods:
                    eval_result = eval(eval_property)

                    if callable(eval_result):
                        eval_function = f"python_object.{i}()"

                        try: print(f"{i}: {eval(eval_function)}")
                        except TypeError: print(f"{i}: {eval(eval_property)}")

                    else: print(f"{i}: {eval_result}")

                else: print(f"{i}: {eval(eval_property)}")

            except AttributeError: print(f"! Unable to get the {i} attribute for the item.")

    def deep_copy(self) -> Any:
        """
        Return a deep (complete, recursive) copy of the given python object."""

        import copy

        return copy.deepcopy(self.object)

    def shallow_copy(self) -> Any:
        """
        Return shallow copy of the given python object."""

        import copy

        return copy.copy(self.object)

    def toString(self) -> str:
        """
        Convert the given python type to a string."""

        return str(self.typeName)

    @property
    def typeName(self) -> str:
        """
        Return the common name of the given type."""

        return type(self.object).__name__

    @property
    def docString(self) -> Union[str, None]:
        """
        Get the doc string for the given python object (e.g. module, function, or class)."""

        import inspect

        return inspect.getdoc(self.object)

    @property
    def sourceCode(self) -> str:
        """
        Get the source code for the given python object (e.g. module, function, or class)."""

        import inspect

        return inspect.getsource(self.object)

    @property
    def sourceFile(self) -> str:
        """
        Get the source file for the given python object (e.g. module, function, or class)."""

        import inspect

        return inspect.getsourcefile(self.object)

    @property
    def signature(self) -> str:
        """
        Get the argument signature for the given python object (e.g. module, function, or class)."""

        import inspect

        return inspect.signature(self.object)


class python_code:
    def __init__(self, code: str): self.code = code

    @property
    def details(self):
        """
        Get details about the given code_text. This is a wrapper for `dis.code_info`"""

        import dis

        return dis.code_info(self.code)

    @property
    def variables(self) -> List[str]:
        """Get all of the variables names in the code_text.
        TODO: add a caveat that this function will only find *stored* variables and not those which are referenced or...
        loaded. E.g., given "x = y + 1", this function will return ["x"]; note that "y" is not included
        """

        return [
            node.id
            for node in ast.walk(
                python_ast_parse(code_text)
            )
            if isinstance(node, ast.Name) and (isinstance(node.ctx, ast.Store))
        ]

    @property
    def constants(self) -> List[str]:
        """Get all constants in the code_text."""

        # TODO: add a caveat that this function will only find *stored* variables which are uppercased
        return [
            var
            for var in python_variable_names(self.code)
            if var.isupper()
        ]

    def functions(self, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False) -> List[str]:
        """."""

        functions = [f.name for f in python_ast_function_defs(self.code, recursive_search=not ignore_nested_functions)]
        return [
            name
            for name in functions
            if not name.startswith('_')
        ] if ignore_private_functions else functions

    def functions_docstrings(self, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False) -> List[str]:
        """Get docstrings for all of the functions in the given text."""

        return [
            ast.get_docstring(f)
            for f in python_ast_function_defs(
                self.code,
                recursive_search=not ignore_nested_functions
            )
            if not (ignore_private_functions and f.name.startswith('_'))
        ]

    def functions_as_importString(self, module_name: str) -> str:
        """."""

        import jinja2

        return jinja2.Template(
            '''from {{ module_name }} import (
                {%- for name in function_names %}
                    {{ name }},
                {%- endfor %}
                )''', autoescape=True
        ).render(
            module_name=module_name,
            function_names=self.functions()
        )

    def clean(self) -> str:
        """
        Clean python code as it is often found in documentation and snippets."""

        self.code = self.code.replace('>>> ', '').replace('... ', '')
        return self.code

    def disassemble(self):
        """
        Disassemble the python code_text. This is a wrapper for `dis.dis`"""

        import dis

        return dis.Bytecode(self.code).dis()

    def get_lines(self, *, ignore_empty_lines: bool = True) -> int:
        """
        Return the number of lines in the given function_text."""

        from d8s_lists import truthy_items

        return len(
            tuple(
                truthy_items(self.code.splitlines())
            )
        ) if ignore_empty_lines else len(
            self.code.splitlines()
        )

    def get_functions_signatures(self, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False, keep_function_name: bool = False, ) -> List[str]:
        """
        Return the function signatures for all of the functions in the given code_text."""

        from d8s_strings import string_remove_from_start
        from .ast import python_function_names
        import re

        signatures = []

        for name in python_function_names(self.code, ignore_private_functions=ignore_private_functions, ignore_nested_functions=ignore_nested_functions):
            regex_for_signature = fr'(def {name}\((?:.|\s)*?\).*?):'
            sig = re.findall(regex_for_signature, self.code)

            if any(sig):
                new_sig = string_remove_from_start(sig[0], 'def ')
                if not keep_function_name: new_sig = string_remove_from_start(new_sig, name)

                signatures.append(new_sig)

        return signatures

    def get_functions_blocks(self, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False) -> List[str]:
        """
        Find the code (as a string) for every function in the given code_text."""

        from d8s_lists import has_index
        from d8s_strings import string_chars_at_start_len

        from .ast import python_ast_function_defs, python_ast_object_line_numbers

        function_block_strings = []

        code_text_as_lines = self.code.splitlines()

        for function_name, (start, end) in [
            (
                f.name, python_ast_object_line_numbers(f)
            )
            for f in python_ast_function_defs(self.code, recursive_search=not ignore_nested_functions)
        ]:
            function_block_lines = code_text_as_lines[start - 1: end]  # noqa=E203
            function_block_string = '\n'.join(function_block_lines)

            """
            The code below checks to see if the line after what was determined to be the last line of the function...
            should also be included in the function block (which is the case when the closing parenthesis of a...
            function call in another function is on a newline (see the...
            python_data_tests.py::test_python_function_blocks_edge_cases_1 for an example))
            """

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

    def get_functions_lengths(self) -> List[int]:
        """
        Find the lengths of each function in the given code_text."""

        return [
            python_code(block).get_lines()
            for block in self.get_functions_blocks()
        ]

    def get_todos(self, todo_regex: str = 'TODO:.*') -> List[str]:
        """
        Return all todos in the given code_text that match the given todo_regex."""

        import re

        return re.findall(todo_regex, self.code)

    def get_fStrings(self, *, include_braces: bool = False) -> Iterator[str]:
        """
        Find all of the python formatted string literals in the given text.

        See https://realpython.com/python-f-strings/ for more details about f-strings.
        """

        from d8s_grammars import python_formatted_string_literal
        from d8s_lists import flatten

        f_strings = flatten(
            python_formatted_string_literal.searchString(self.code).asList()
        )

        return f_strings if include_braces else (
            string.strip('{').strip('}')
            for string in f_strings
        )

    def get_imports(self) -> Dict[str, List[str]]:
        """
        Return a dictionary containing the names of all imported modules.
        Start with the Import nodes.
        These will always have an empty list of submodules
        so we can just overwrite them without losing any data
        """

        from ast import Import, ImportFrom
        from .ast import python_ast_objects_of_type

        modules = {
            alias.name: []
            for node in python_ast_objects_of_type(self.code, Import)
            for alias in node.names
        }

        # Now for the ImportFrom nodes
        [
            modules.setdefault(
                "." * node.level if node.module is None else node.module, []
            ).append(alias.name)
            for node in python_ast_objects_of_type(self.code, ImportFrom)
            for alias in node.names
        ]

        return modules

    def exceptions_handled(self) -> Iterable[str]:
        """Return a list of all exceptions handled in the given code."""

        from .ast import python_ast_exceptions, python_ast

        yield from more_itertools.collapse(
            list(
                map(
                    lambda handler: python_ast_exceptions(None, handler).exceptions_handled_by_handler,
                    python_ast(self.code).get_astObjects_by_type(ast.ExceptHandler)
                )
            ), base_type=str
        )

    def exceptions_raised(self) -> Iterable[str]:
        """Return a list of all exceptions raised in the given code."""

        from .ast import python_ast, python_ast_exceptions

        code = python_ast(self.code)

        exceptions = list(
            map(
                lambda handler: python_ast_exceptions(None, handler).exceptions_raised_by_handler,
                python_ast(code.parse()).get_astObjects_by_type(ast.ExceptHandler)
            )
        )
        """
        Remove all of the ast.ExceptHandlers so exceptions are not parsed twice...
        (once from the code above and once in the code below)
        """

        exceptions.extend(
            list(
                map(
                    lambda obj: python_ast_exceptions(None, obj).name,
                    (
                        node
                        for node in python_ast(code.parse()).get_opposite_astObjects_by_type(ast.ExceptHandler)
                        if isinstance(node, ast.Raise)
                    )
                )
            )
        )

        yield from more_itertools.collapse(
            exceptions,
            base_type=str
        )


class python_variables:
    def __init__(self, variable: str): self.variable = variable

    @property
    def asPythonic(self) -> str:
        """
        Make the name pythonic.

        (e.g. 'fooBar' => 'foo_bar', 'foo-bar' => 'foo_bar', 'foo bar' => 'foo_bar', 'Foo Bar' => 'foo_bar').
        """

        from d8s_strings import lowercase, snake_case, string_split_on_uppercase

        return snake_case(
            lowercase(
                '_'.join(
                    [
                        string.strip()
                        for string in string_split_on_uppercase(self.variable, include_uppercase_characters=True, split_acronyms=False)
                    ]
                )
            )
        )


class python_traceback:
    def __init__(self, traceback: str): self.traceback = traceback

    def prettify(self) -> str:
        """
        Return a string with the given traceback pretty-printed."""

        import re

        return re.sub(' File ', '\nFile ', self.traceback)

    def pretty_print(self) -> None:
        """
        Return a string with the given traceback pretty-printed."""

        print(
            self.prettify()
        )


class python_versioning:
    @staticmethod
    def version( ) -> str:
        """
        Return the python version of the current environment."""

        import sys

        return ".".join(
            [
                sys.version_info.major.__str__(),
                sys.version_info.minor.__str__(),
                sys.version_info.micro.__str__()
            ]
        )

    @staticmethod
    def isVersion2( ) -> bool:
        """
        Return whether or not the python version of the current environment is v2.x."""

        return int(
            python_versioning.version()[0]
        ) == 2

    @staticmethod
    def isVersion3( ) -> bool:
        """
        Return whether or not the python version of the current environment is v3.x."""

        return int(
            python_versioning.version()[0]
        ) == 3


class python_files_and_directories:
    def __init__(self, directory_path: str): self.directory = directory_path

    def get_pyFiles(self, *, exclude_tests: bool = False) -> List[str]:  # noqa: CCR001
        """
        Find all python files in the given directory."""

        from d8s_file_system import directory_file_names_matching

        return [
            file
            for file in directory_file_names_matching(self.directory, '*.py')
            if '_test' not in file and 'test_' not in file
        ] if exclude_tests else directory_file_names_matching(self.directory, '*.py')

    def get_files_using_function(self, func: str) -> List[str]:
        """
        Find where the given function is used in the given search path."""

        from d8s_file_system import directory_read_files_with_path_matching

        return [
            file
            for file, content in directory_read_files_with_path_matching(self.directory, '*.py')
            if f"{func}(" in content
        ]


class python_enviroments:
    @property
    def stacked_local_data(self):
        """
        Get local data in the current python environment."""

        import inspect

        return inspect.currentframe().f_locals


def namespace_has_argument(namespace: argparse.Namespace, argument_name: str) -> bool:
    """."""

    return argument_name in namespace


# TODO: need to standardize the order of arguments between functions like this an the directorySearch function
# TODO: improve the type annotations to be lists of types
def sort_type_list_by_name(type_list: List[type], **kwargs) -> List[type]:
    """."""

    return sorted(
        type_list,
        key=lambda x: python_objects(x).typeName,
        **kwargs
    )
