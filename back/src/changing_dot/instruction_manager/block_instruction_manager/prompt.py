system_prompt = """You are a specialized software engineer.
Your role is to give precise baby step instructions. You have a selection of actions that you can take, them you can apply them on a specific file and line_number. You give a specific importance to limiting the scope of your changes and only give the next baby step change."""


prompt = """
Our overall goal is to {goal}
After a few steps, we arrived here :
The following file change {cause_edits} caused the following ERROR :
{error}

Here are the possible blocks that you can use :
{blocks}

What is the easiest most straitforward way to fix this error.
Please prefer "replace" changes rather than adds or removes
Please add the line number to change in your response
{failed_attempts}
Please answer using the following format :
"
Block: <int that is the id of the affected block>
Instruction: <Your instructions on how to change this block to solve the issue>
"
"""
