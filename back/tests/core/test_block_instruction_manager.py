from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    BlockInstructionManager,
    InstructionBlock,
)
from langchain_community.chat_models.fake import FakeListChatModel

model = FakeListChatModel(
    responses=[
        """Block: 1
Instructions: Do what you like bro
you know"""
    ]
)


def test_basic_instruction() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/instruction_manager/basic_file.cs"])
    G = ChangingGraph()
    goal = "We want to be more original in the output of our method"

    G.add_problem_node(
        {
            "index": 0,
            "node_type": "problem",
            "status": "pending",
            "error": {
                "text": "This is Hello World, it is not original",
                "file_path": "./tests/core/fixtures/instruction_manager/basic_file.cs",
                "pos": (5, 0, 5, 0),
                "project_name": "Initial project",
            },
        }
    )

    intruction_manager_SUT = BlockInstructionManager(model, goal)

    instruction = intruction_manager_SUT.get_node_instruction(G, DG, 0)

    assert instruction == InstructionBlock(
        block_id=1,
        file_path="./tests/core/fixtures/instruction_manager/basic_file.cs",
        solution="""Do what you like bro
you know""",
    )
