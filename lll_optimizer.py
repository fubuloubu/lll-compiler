from typing import Dict, Optional, Set

import inspect
import sys

from errors import CompilerError
from node_utils import NodeMutator

import lll_ast
from lll_compiler import VM, AVAILABLE_VMS, DEFAULT_VM


optimization_1: NodeMutator = NodeMutator(lll_ast.LLLNode)


@optimization_1.register(lll_ast.LLLNode)
def optimize_Node(node: lll_ast.LLLNode, vm: VM) -> lll_ast.LLLNode:
    return node


# Used to select/de-select optimizations to run
OPTIMIZATIONS: Dict[str, NodeMutator] = {
    optimization.lower(): optimization
    for optimization_name, optimization in inspect.getmembers(
        sys.modules[__name__], predicate=lambda o: isinstance(o, NodeMutator)
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
                node = optimization.update(node, vm)

    return node
