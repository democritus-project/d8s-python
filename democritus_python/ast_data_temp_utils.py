from typing import Any, Iterable, Tuple


def list_item_indexes(list_arg: list, item: Any) -> Tuple[int, ...]:
    """Find the given item in the iterable. Return -1 if the item is not found."""
    indexes = [index for index, value in enumerate(list_arg) if value == item]
    return indexes


def list_delete_item(list_arg: list, item_to_delete: Any) -> list:
    """Remove all instances of the given item_to_delete from the list_arg."""
    from itertools import filterfalse

    result = list(filterfalse(lambda x: x == item_to_delete, list_arg))
    return result


def list_replace(list_arg: list, old_value, new_value, *, replace_in_place: bool = True) -> list:
    """Replace all instances of the old_value with the new_value in the given list_arg."""
    old_value_indexes = list_item_indexes(list_arg, old_value)
    new_list = list_delete_item(list_arg, old_value)

    for index in old_value_indexes:
        if replace_in_place:
            new_list.insert(index, new_value)
        else:
            new_list.append(new_value)

    return new_list


def list_delete_empty_items(list_arg: list) -> list:
    """Delete items from the list_arg is the item is an empty strings, empty list, zero, False or None."""
    empty_values = ('', [], 0, False, None)
    # TODO: not sure if this is the right way to implement this
    return [i for i in list_arg if i not in empty_values]
