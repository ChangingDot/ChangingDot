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
    last_operator = ""
    number_of_operator_switchs = 0
    for line in lines:
        if line.strip().startswith("---") or line.strip().startswith("+++"):
            continue

        if line.strip().startswith("-"):
            # if switch
            if last_operator == "+":
                number_of_operator_switchs += 1

                if number_of_operator_switchs % 2 == 0:
                    # save current hunk
                    if len(hunk) > 0:
                        hunks.append(hunk)
                    # reset hunk
                    hunk = ""

            hunk = hunk + line
            last_operator = "-"

        elif line.strip().startswith("+"):
            if last_operator == "-":
                number_of_operator_switchs += 1

                if number_of_operator_switchs % 2 == 0:
                    # save current hunk
                    if len(hunk) > 0:
                        hunks.append(hunk)
                    # reset hunk
                    hunk = ""

            hunk = hunk + line
            last_operator = "+"
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
        if hunk_line.strip()[0] == "-":
            before = before + hunk_line.replace("-", "", 1)
        elif hunk_line.strip()[0] == "+":
            after = after + hunk_line.replace("+", "", 1)
    if before.endswith("\n"):
        before = before[:-1]
    if after.endswith("\n"):
        after = after[:-1]
    return ProcessedDiff(before=before, after=after)
