from typing import TYPE_CHECKING

from core.utils.list_action_applier import apply_actions_on_list

if TYPE_CHECKING:
    from core.utils.list_action_applier import Action


def test_empty_action_applier() -> None:
    input_list = ["a", "b", "c", "d"]
    actions: list[Action] = []
    assert apply_actions_on_list(input_list, actions) == ["a", "b", "c", "d"]


def test_add_action_applier() -> None:
    input_list = ["a", "b", "c", "d"]
    actions: list[Action] = [
        {
            "action_type": "add",
            "line_number": 2,
            "after": "here",
        }
    ]
    assert apply_actions_on_list(input_list, actions) == ["a", "here", "b", "c", "d"]


def test_remove_action_applier() -> None:
    input_list = ["a", "b", "c", "d"]
    actions: list[Action] = [
        {
            "action_type": "remove",
            "line_number": 2,
            "after": "",
        }
    ]
    assert apply_actions_on_list(input_list, actions) == ["a", "c", "d"]


def test_replace_action_applier() -> None:
    input_list = ["a", "b", "c", "d"]
    actions: list[Action] = [
        {
            "action_type": "replace",
            "line_number": 2,
            "after": "B",
        }
    ]
    assert apply_actions_on_list(input_list, actions) == ["a", "B", "c", "d"]


def test_add_end_action_applier() -> None:
    input_list = ["a", "b", "c", "d"]
    actions: list[Action] = [
        {
            "action_type": "add",
            "line_number": 5,
            "after": "here",
        }
    ]
    assert apply_actions_on_list(input_list, actions) == ["a", "b", "c", "d", "here"]


def test_multiple_add_end_action_applier() -> None:
    input_list = ["a", "b", "c", "d"]
    actions: list[Action] = [
        {
            "action_type": "add",
            "line_number": 5,
            "after": "1",
        },
        {
            "action_type": "add",
            "line_number": 6,
            "after": "2",
        },
        {
            "action_type": "add",
            "line_number": 7,
            "after": "3",
        },
    ]
    assert apply_actions_on_list(input_list, actions) == [
        "a",
        "b",
        "c",
        "d",
        "1",
        "2",
        "3",
    ]


def test_remove_first_action_applier() -> None:
    input_list = ["a", "b", "c", "d"]
    actions: list[Action] = [
        {
            "action_type": "remove",
            "line_number": 1,
            "after": "",
        }
    ]
    assert apply_actions_on_list(input_list, actions) == ["b", "c", "d"]


def test_replace_end_action_applier() -> None:
    input_list = ["a", "b", "c", "d"]
    actions: list[Action] = [
        {
            "action_type": "replace",
            "line_number": 4,
            "after": "D",
        }
    ]
    assert apply_actions_on_list(input_list, actions) == ["a", "b", "c", "D"]


def test_add_then_replace_action_applier() -> None:
    input_list = ["a", "b", "c", "d"]
    actions: list[Action] = [
        {
            "action_type": "add",
            "line_number": 1,
            "after": "here",
        },
        {
            "action_type": "replace",
            "line_number": 4,
            "after": "D",
        },
    ]
    assert apply_actions_on_list(input_list, actions) == ["here", "a", "b", "c", "D"]


def test_multiple_adds_actions_applier() -> None:
    input_list = ["init"]
    actions: list[Action] = [
        {
            "action_type": "add",
            "line_number": 1,
            "after": "1",
        },
        {
            "action_type": "add",
            "line_number": 1,
            "after": "2",
        },
        {
            "action_type": "add",
            "line_number": 1,
            "after": "3",
        },
    ]
    assert apply_actions_on_list(input_list, actions) == ["1", "2", "3", "init"]


def test_multiple_actions_applier() -> None:
    input_list = ["a", "b", "c", "d", "e", "f"]
    actions: list[Action] = [
        {
            "action_type": "add",
            "line_number": 1,
            "after": "here",
        },
        {
            "action_type": "replace",
            "line_number": 4,
            "after": "D",
        },
        {
            "action_type": "remove",
            "line_number": 2,
            "after": "",
        },
        {
            "action_type": "replace",
            "line_number": 3,
            "after": "C",
        },
        {
            "action_type": "add",
            "line_number": 1,
            "after": "1",
        },
        {
            "action_type": "add",
            "line_number": 1,
            "after": "2",
        },
        {
            "action_type": "replace",
            "line_number": 6,
            "after": "F",
        },
    ]
    assert apply_actions_on_list(input_list, actions) == [
        "here",
        "1",
        "2",
        "a",
        "C",
        "D",
        "e",
        "F",
    ]
