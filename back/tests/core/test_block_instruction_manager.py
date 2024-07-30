from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    BlockInstructionManager,
    InstructionBlock,
)
from langchain_community.chat_models.fake import FakeListChatModel


def test_basic_instruction() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/instruction_manager/basic_file.cs"])
    G = ChangingGraph()
    goal = "We want to be more original in the output of our method"
    model = FakeListChatModel(
        responses=[
            """Block: 1
Instructions: Do what you like bro
you know"""
        ]
    )

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


def test_with_multiple_blocks_instruction() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/instruction_manager/basic_change.cs"])
    G = ChangingGraph()
    goal = "We want to change ChangedSize to Size"

    model = FakeListChatModel(
        responses=[
            """
                Block: 7
    Instruction: Change line 26 from `public int ChangedSize { get; set; }` to `public int Size { get; set; }`"""
        ]
    )

    G.add_problem_node(
        {
            "index": 0,
            "node_type": "problem",
            "status": "pending",
            "error": {
                "text": "ChangedSize does not exist",
                "file_path": "./tests/core/fixtures/instruction_manager/basic_change.cs",
                "pos": (26, 0, 26, 0),
                "project_name": "Initial project",
            },
        }
    )

    intruction_manager_SUT = BlockInstructionManager(model, goal)

    instruction = intruction_manager_SUT.get_node_instruction(G, DG, 0)

    assert instruction == InstructionBlock(
        block_id=7,
        file_path="./tests/core/fixtures/instruction_manager/basic_change.cs",
        solution="Change line 26 from `public int ChangedSize { get; set; }` to `public int Size { get; set; }`",
    )
