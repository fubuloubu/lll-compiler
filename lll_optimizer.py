from errors import CompilerError
from node_utils import ExplorationError, NodeOptimizer
from evm_asm import evm_opcodes, LATEST_VERSION  # type: ignore

import lll_ast


optimizer: NodeOptimizer = NodeOptimizer(lll_ast.LLLNode)


def optimize(
    node: lll_ast.LLLNode, version: str = LATEST_VERSION, num_iterations: int = 200
) -> lll_ast.LLLNode:
    if version not in evm_opcodes:
        raise CompilerError(f"Fork '{version}' is not supported")

    vm = evm_opcodes[version]

    for _ in range(num_iterations):
        try:
            node = optimizer.update(node, vm)
        except ExplorationError as e:
            raise CompilerError("Optimization Failed") from e

        if node is None:
            raise CompilerError("Optimization Failed")

    return node
