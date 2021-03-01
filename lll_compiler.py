from eth_utils import to_bytes

from evm_asm import evm_opcodes, LATEST_VERSION  # type: ignore
from evm_asm.assembler import assemble  # type: ignore
from evm_asm.forks import Fork  # type: ignore
from evm_asm.typing import Assembly  # type: ignore

from node_utils import NodeTransformer

import lll_ast

from errors import CompilerError
from lll_parser import parse


class CompileContext:
    def __init__(self, vm: Fork):
        self.vm = vm
        self.vars: dict = {"~codelen": lll_ast.Num(0)}

    def create_var(self, name: lll_ast.Var, val: lll_ast.LLLNode):
        assert name not in self.vars, "No shadowing allowed"
        self.vars[name] = val


Compiler = NodeTransformer[CompileContext, Assembly]
compiler: Compiler = NodeTransformer(lll_ast.LLLNode)


@compiler.register(lll_ast._NullOp)
def compile_NullOp(node: lll_ast._NullOp, ctx: CompileContext) -> Assembly:
    return [ctx.vm[node.type.upper()]]


@compiler.register(lll_ast.Num)
def compile_Num(node: lll_ast.Num) -> Assembly:
    return [to_bytes(node.value)]


@compiler.register(lll_ast.With)
def compile_With(node: lll_ast.With, ctx: CompileContext) -> Assembly:
    ctx.create_var(node.variable, node.value)
    return compiler.transform(node.value, ctx)


@compiler.register(lll_ast.Var)
def compile_Var(node: lll_ast.Var, ctx: CompileContext) -> Assembly:
    return compile_Num(ctx.vars[node.name])


@compiler.register(lll_ast.Seq)
def compile_Seq(node: lll_ast.Seq, ctx: CompileContext) -> Assembly:
    asm = []  # type: ignore

    for stmt in node.statements:
        asm.extend(compiler.transform(stmt, ctx))

    return asm


@compiler.register(lll_ast.Call)
def compile_Call(node: lll_ast.Call, ctx: CompileContext) -> Assembly:
    return [
        *compiler.transform(node.gas_limit, ctx),
        *compiler.transform(node.address, ctx),
        *compiler.transform(node.value, ctx),
        *compiler.transform(node.args_offset, ctx),
        *compiler.transform(node.args_length, ctx),
        *compiler.transform(node.return_offset, ctx),
        *compiler.transform(node.return_length, ctx),
        ctx.vm.CALL,  # type: ignore
    ]


@compiler.register(lll_ast.StaticCall)
def compile_StaticCall(node: lll_ast.StaticCall, ctx: CompileContext) -> Assembly:
    return [
        *compiler.transform(node.gas_limit, ctx),
        *compiler.transform(node.address, ctx),
        *compiler.transform(node.args_offset, ctx),
        *compiler.transform(node.args_length, ctx),
        *compiler.transform(node.return_offset, ctx),
        *compiler.transform(node.return_length, ctx),
        ctx.vm.STATICCALL,  # type: ignore
    ]


@compiler.register(lll_ast._UnaryOp)
def compile_UnaryOp(node: lll_ast._UnaryOp, ctx: CompileContext) -> Assembly:
    return [
        *compiler.transform(node.operand, ctx),
        ctx.vm[node.type.upper()],
    ]


@compiler.register(lll_ast._BinOp)
def compile_BinOp(node: lll_ast._BinOp, ctx: CompileContext) -> Assembly:
    return [
        *compiler.transform(node.rhs, ctx),
        *compiler.transform(node.lhs, ctx),
        ctx.vm[node.type.upper()],
    ]


@compiler.register(lll_ast.Shr)
def compile_Shr(node: lll_ast.Shr, ctx: CompileContext) -> Assembly:
    return [
        *compiler.transform(node.operand, ctx),
        *compiler.transform(node.bits, ctx),
        ctx.vm.SHR,  # type: ignore
    ]


@compiler.register(lll_ast.Shl)
def compile_Shl(node: lll_ast.Shl, ctx: CompileContext) -> Assembly:
    return [
        *compiler.transform(node.operand, ctx),
        *compiler.transform(node.bits, ctx),
        ctx.vm.SHL,  # type: ignore
    ]


@compiler.register(lll_ast.CodeLoad)
def compile_CodeLoad(node: lll_ast.CodeLoad, ctx: CompileContext) -> Assembly:
    return [
        *compiler.transform(node.length, ctx),
        ctx.vm.CODELOAD,  # type: ignore
    ]


@compiler.register(lll_ast.CodeCopy)
def compile_CodeCopy(node: lll_ast.CodeCopy, ctx: CompileContext) -> Assembly:
    return [
        *compiler.transform(node.register, ctx),
        *compiler.transform(node.pointer, ctx),
        *compiler.transform(node.length, ctx),
        ctx.vm.CODECOPY,  # type: ignore
    ]


def compile(node: lll_ast.LLLNode, version: str = None) -> Assembly:
    if version and version not in evm_opcodes.forks():
        raise CompilerError(f"Fork '{version}' is not supported")

    ctx = CompileContext(evm_opcodes[version] if version else LATEST_VERSION)
    return compiler.transform(node, ctx)


if __name__ == "__main__":
    import sys

    program = "".join(sys.stdin)
    ast = parse(program)
    if ast is None:
        print("Failed to compile")

    asm = compile(ast)
    bytecode = assemble(LATEST_VERSION, asm)
    print("0x" + bytecode.hex())
