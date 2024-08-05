from pydantic import BaseModel


class ProcessedDiff(BaseModel):
    before: str
    after: str


def process_diff(diff: str) -> list[ProcessedDiff]:
    hunks = extract_hunks(diff)
    return [process_hunk(hunk) for hunk in hunks]


def extract_hunks(diff: str) -> list[str]:
    hunks = []

    lines = diff.splitlines(keepends=True)

    hunk = ""
    for line in lines:
        if (
            line.strip().startswith("-")
            and not line.strip().startswith("---")
            or line.strip().startswith("+")
            and not line.strip().startswith("+++")
        ):
            hunk = hunk + line
        else:
            # stop this hunk and start new one
            if len(hunk) > 0:
                hunks.append(hunk)
            hunk = ""

    return hunks


def process_hunk(hunk: str) -> ProcessedDiff:
    before = ""
    after = ""
    hunk_lines = hunk.splitlines(keepends=True)
    for hunk_line in hunk_lines:
        if hunk_line[0] == "-":
            before = before + hunk_line[1:]
        elif hunk_line[0] == "+":
            after = after + hunk_line[1:]
    # [:-1] to remove last \n
    return ProcessedDiff(before=before[:-1], after=after[:-1])
