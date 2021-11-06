import ast
from typing import Iterable, List, Optional, Tuple


# TODO: all of these functions where code_text is given should also be able to read a file at a given path (?)
class python_ast_exceptions:
    def __init__(self, exception: ast.Raise, exception_handler: ast.ExceptHandler): self.exception = exception; self.exception_handler = exception_handler

    @property
    def name(self) -> str:  # noqa: CCR001
        """."""

        if hasattr(self.exception, 'exc') and self.exception.exc:  # this handles ast.Raise nodes
            if hasattr(
                self.exception.exc, 'id'
            ):  # this handles ast.Raise nodes where the exception being raised is an ast.Name (e.g. "e" or "ValueError")
                return self.exception.exc.id
            elif hasattr(
                self.exception.exc.func, 'id'
            ):  # handles ast.Raise nodes where the exception being raised is an ast.Call (e.g. "ValueError('Foo Bar')")
                return self.exception.exc.func.id
            elif hasattr(
                self.exception.exc.func, 'attr'
            ):  # this handles ast.Raise nodes raising a non-built-in error (e.g. "pint.UndefinedUnitError")
                return f'{self.exception.exc.func.value.id}.{self.exception.exc.func.attr}'
        elif hasattr(self.exception, 'type') and self.exception.type:  # this handles ast.ExceptHandler nodes
            if hasattr(
                self.exception.type, 'id'
            ):  # this handles ast.ExceptHandler nodes raising a built-in error (e.g. "RuntimeError")
                return self.exception.type.id
            elif hasattr(
                self.exception.type, 'attr'
            ):  # this handles ast.ExceptHandler nodes raising a non-built-in error (e.g. "pint.UndefinedUnitError")
                return f'{self.exception.type.value.id}.{self.exception.type.attr}'
        elif hasattr(
            self.exception, 'attr'
        ):  # this handles situations where the exception being raised is an ast.Attribute (e.g. "pint.UndefinedUnitError")
            return f'{self.exception.value.id}.{self.exception.attr}'
        elif hasattr(self.exception, 'id'):  # this handles situations where the exception being raised is an ast.Name (e.g. "e")
            return self.exception.id

    @property
    def exceptions_handled_by_handler(self) -> Optional[Iterable[str]]:
        """Return all of the exceptions handled by the given exception handler."""

        if self.exception_handler.type and hasattr(self.exception_handler.type, 'elts'):
            yield from (
                python_ast_exceptions(i, None).name
                for i in self.exception_handler.type.elts
            )

        elif exception_name := python_ast_exceptions(self.exception_handler, None).name: yield exception_name

    @property
    def exceptions_raised_by_handler(self) -> Optional[Iterable[str]]:
        """Return the exception raised by the given exception handler."""

        from d8s_lists import iterable_replace

        exceptions_names = list(map(python_ast_raise_name, python_ast(self.exception_handler).get_astObjects_by_type(ast.Raise)))

        for name in exceptions_names:
            if name == handler.name:
                exceptions_names = iterable_replace(
                    exceptions_names,
                    name,
                    self.exceptions_handled
                )
            elif name is None:
                exceptions_names = iterable_replace(
                    exceptions_names,
                    name,
                    self.exceptions_handled
                )

        import more_itertools

        yield from more_itertools.collapse(
            exceptions_names,
            base_type=str
        )


class python_ast:
    def __init__(self, astree: object): self.astree = astree

    def clean(self) -> str:
        """."""

        import re

        return re.sub('\n', '\\\\n', self.astree)

    def parse(self) -> ast.Module:
        """."""

        try: return ast.parse(self.astree)
        except Exception: return ast.parse(self.clean())

    def get_lines(self) -> Tuple[int, int]:
        """."""

        from d8s_algorithms import depth_first_traverse
        from d8s_lists import truthy_items

        line_numbers = tuple(
            truthy_items(
                list(
                    depth_first_traverse(
                        self.astree, ast.iter_child_nodes, collect_items_function=python_ast_object_line_number
                    )
                )
            )
        )
        return min(line_numbers), max(line_numbers)

    def get_line_number(self) -> Optional[int]:
        """."""

        return self.astree.lineno if hasattr(self.astree, 'lineno') else None

    # TODO: have a decorator to parse a first argument that is a string
    def get_astObjects_by_type(self, ast_type: type, *, recursive_search: bool = True) -> Iterable[object]:
        """Return all of the ast objects of the given ast_type in the code_text_or_ast_object."""

        parsed_code = self.parse() if isinstance(self.astree, str) else self.astree

        if recursive_search:
            yield from (
                node
                for node in ast.walk(parsed_code)
                if isinstance(node, ast_type)
            )

        else:
            if isinstance(parsed_code, ast_type): yield parsed_code

            if hasattr(parsed_code, 'body'):
                yield from (
                    node
                    for node in parsed_code.body
                    if isinstance(node, ast_type)
                )

    def get_opposite_astObjects_by_type(self, ast_type: type) -> Iterable[object]:
        """Return all of the ast objects which are not of the given ast_type in the code_text_or_ast_object."""

        from d8s_algorithms import depth_first_traverse

        """
        ast_objects_not_of_type = (node for node in ast.walk(parsed_code) if not isinstance(node, ast_type))
        for node in ast.walk(parsed_code):
            if not isinstance(node, ast_type):
                yield node
            else:
                break

        return ast_objects_not_of_type
        """

        from d8s_lists import truthy_items

        return truthy_items(
            list(
                depth_first_traverse(
                    python_ast_parse(self.astree) if isinstance(self.astree, str) else self.astree,
                    lambda x: ast.iter_child_nodes(x) if not isinstance(x, ast_type) else [],
                    collect_items_function=lambda x: x,
                )
            )
        )

    def get_functions_defs(self, recursive_search: bool = True) -> Iterable[ast.FunctionDef]:
        """."""

        yield from self.get_astObjects_by_type(ast.FunctionDef, recursive_search=recursive_search)
        yield from self.get_astObjects_by_type(ast.AsyncFunctionDef, recursive_search=recursive_search)

    def get_functions_arguments(self) -> List[ast.arg]:
        """."""

        return self.parse().body[0].args.args

    def get_functions_arguments_names(self) -> Iterable[str]:
        """."""

        return (
            arg.arg
            for arg in self.get_functions_arguments()
        )

    def get_functions_arguments_defaults(self) -> List[str]:
        """."""

        # TODO: this function does not return defaults for keyword args
        return self.parse().body[0].args.defaults

    def get_functions_arguments_annotations(self) -> List[str]:
        """."""

        return [
            arg.annotation.id
            for arg in self.get_functions_arguments()
            if arg.annotation
        ]
