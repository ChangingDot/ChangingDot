from changing_dot.custom_types import BlockEdit


def reverse_edits(edits: list[BlockEdit]) -> list[BlockEdit]:
    return [
        BlockEdit(
            block_id=edit.block_id,
            file_path=edit.file_path,
            before=edit.after,
            after=edit.before,
        )
        for edit in edits
    ]
