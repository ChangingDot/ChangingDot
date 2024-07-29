from changing_dot.custom_types import Edits
from changing_dot.error_manager.error_manager import (
    IErrorManager,
)
from changing_dot.modifyle.modifyle import applied_edits_context


def check_solution_syntax_correctness(
    edits: Edits,
    error_manager: IErrorManager,
) -> bool:
    with applied_edits_context(edits):
        has_syntax_errors = error_manager.has_syntax_errors()
    return not has_syntax_errors
