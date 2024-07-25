system_prompt = """You are a specialized software engineer.
Your role is to give precise baby step instructions. You have a selection of actions that you can take, them you can apply them on a specific file and line_number. You give a specific importance to limiting the scope of your changes and only give the next baby step change."""


prompt = """
Our overall goal is to {goal}
After a few steps, we arrived here :
The following file change caused the following ERROR :
{prompt_diff}

What is the easiest most straitforward way to fix this error.
Please add the line number to change in your response
{failed_attempts}
"""


def make_format_prompt(actions: str) -> str:
    return f"""Please answer in JSON following this schema. Please do not use code blocks in the json :
edit_type : str ->What action did the programmer choose to take out of the following {actions} (those outside of this will not work and break production)
line_number : int -> On what line should the action take place ?
solution: str -> Description of the next step
Only write one change, do NOT use a list.
"""
