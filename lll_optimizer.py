from typing import Dict, Set

import inspect
import sys

from errors import CompilerError
from node_utils import ExplorationError, NodeOptimizer

import lll_ast
from lll_compiler import VM, AVAILABLE_VMS, DEFAULT_VM


optimization_1: NodeOptimizer = NodeOptimizer(lll_ast.LLLNode)


@optimization_1.register(lll_ast.LLLNode)
def optimize_Node(node: lll_ast.LLLNode, vm: VM) -> lll_ast.LLLNode:
    return node


# Used to select/de-select optimizations to run
OPTIMIZATIONS: Dict[str, NodeOptimizer] = {
    optimization.lower(): optimization
    for optimization_name, optimization in inspect.getmembers(
        sys.modules[__name__], predicate=lambda o: isinstance(o, NodeOptimizer)
    )
}


def optimize(
    node: lll_ast.LLLNode,
    version: str = DEFAULT_VM,
    num_iterations: int = 200,
    skip_optimizations: Set[str] = None,
) -> lll_ast.LLLNode:
    if version not in AVAILABLE_VMS.keys():
        raise CompilerError(f"Fork '{version}' is not supported")

    vm = AVAILABLE_VMS[version]

    if skip_optimizations is None:
        skip_optimizations = set()

    for _ in range(num_iterations):
        for name, optimization in OPTIMIZATIONS.items():
            if name not in skip_optimizations:
                try:
                    optimized_node = optimization.update(node, vm)
                except ExplorationError as e:
                    raise CompilerError("Optimization Failed") from e

                if optimized_node is None:
                    raise CompilerError("Optimization Failed")
                else:
                    node = optimized_node

    return node
