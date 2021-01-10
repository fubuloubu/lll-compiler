from typing import Dict, List

import inspect
import re

from eth.vm import forks
from eth.vm.base import VM
from eth.vm.opcode import OpcodeAPI

from errors import CompilerError
from node_utils import NodeTransformer

import lll_ast

Assembly = List[OpcodeAPI]
Opcodes = Dict[str, OpcodeAPI]
Compiler = NodeTransformer[lll_ast.LLLNode, Assembly, Opcodes]
compiler: Compiler = NodeTransformer(lll_ast.LLLNode)


@compiler.register(lll_ast._BinOp)
def compile_BinOp(node: lll_ast._BinOp, opcodes: Opcodes) -> Assembly:
    return [
        *compiler.transform(node.rhs, opcodes),
        *compiler.transform(node.lhs, opcodes),
        opcodes[node.type.upper()],  # getattr would be better
    ]


_pattern = re.compile(r"(?<!^)(?=[A-Z])")
AVAILABLE_VMS: Dict[str, VM] = {
    _pattern.sub("_", vm_name[:-2]).lower(): vm
    for vm_name, vm in inspect.getmembers(forks, predicate=inspect.isclass)
}
DEFAULT_VM = "istanbul"


def compile(node: lll_ast.LLLNode, version: str = DEFAULT_VM) -> Assembly:
    if version not in AVAILABLE_VMS.keys():
        raise CompilerError(f"Fork '{version}' is not supported")

    vm_class = AVAILABLE_VMS[version]
    opcode_registry = vm_class._state_class.computation_class.opcodes
    opcodes = {opcode.mnemonic: opcode for opcode in opcode_registry.values()}
    return compiler.transform(node, opcodes)
