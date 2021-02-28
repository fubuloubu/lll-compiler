from typing import Dict, List, Optional, Union

import inspect
import sys

from node_utils import BaseNode, node_type


@node_type
class LLLNode(BaseNode):
    def __str__(self):
        node_type = self.type.lower()

        def stringify_value(v):
            if isinstance(v, list):
                return " ".join(str(i) for i in v)
            else:
                return str(v)

        attrs = " ".join(stringify_value(v) for _, v in self.iter_attributes())
        return f"({node_type} {attrs})" if attrs else node_type


@node_type
class Num(LLLNode):
    value: int

    def __str__(self):
        return str(self.value)


@node_type
class Var(LLLNode):
    name: str

    def __str__(self):
        return self.name


Value = Union[Num, Var, LLLNode]


@node_type
class Call(LLLNode):
    gas_limit: Value
    address: Value
    value: Value
    args_offset: Value
    args_length: Value
    return_offset: Value
    return_length: Value


@node_type
class StaticCall(LLLNode):
    gas_limit: Value
    address: Value
    args_offset: Value
    args_length: Value
    return_offset: Value
    return_length: Value


@node_type
class Set(LLLNode):
    statements: List[LLLNode]


@node_type
class Seq(LLLNode):
    statements: List[LLLNode]


# NOTE: This node is sometimes present, it's an alias
# TODO: Delete this node
@node_type
class Lll(Seq):
    pass


# NOTE: This node is sometimes present, it's an alias
# TODO: Delete this node
@node_type
class Seq_Unchecked(Seq):
    pass


@node_type
class With(LLLNode):
    variable: Var
    value: Value
    statement: Value


@node_type
class Return(LLLNode):
    pointer: Value
    length: Value


@node_type
class Revert(LLLNode):
    pointer: Value
    length: Value


@node_type
class If(LLLNode):
    condition: Value
    true: Value
    false: Optional[Value] = None


@node_type
class Caller(LLLNode):
    pass


@node_type
class Pass(LLLNode):
    pass


@node_type
class Stop(LLLNode):
    pass


@node_type
class Gas(LLLNode):
    pass


@node_type
class CodeSize(LLLNode):
    pass


@node_type
class CalldataSize(LLLNode):
    pass


@node_type
class ReturndataSize(LLLNode):
    pass


@node_type
class _UnaryOp(LLLNode):
    operand: Value


@node_type
class Not(_UnaryOp):
    pass


@node_type
class Clamp_NonZero(_UnaryOp):
    pass


@node_type
class IsZero(_UnaryOp):
    pass


@node_type
class Ceil32(_UnaryOp):
    pass


@node_type
class ExtCodeSize(_UnaryOp):
    pass


@node_type
class ExtCodeHash(_UnaryOp):
    pass


@node_type
class SelfDestruct(_UnaryOp):
    pass


@node_type
class _BinOp(LLLNode):
    lhs: Value
    rhs: Value


@node_type
class Eq(_BinOp):
    pass


@node_type
class Ne(_BinOp):
    pass


@node_type
class Ge(_BinOp):
    pass


@node_type
class Sge(_BinOp):
    pass


@node_type
class Gt(_BinOp):
    pass


@node_type
class Le(_BinOp):
    pass


@node_type
class Lt(_BinOp):
    pass


@node_type
class Slt(_BinOp):
    pass


@node_type
class Sgt(_BinOp):
    pass


@node_type
class UClampLt(_BinOp):
    pass


@node_type
class Or(_BinOp):
    pass


@node_type
class And(_BinOp):
    pass


@node_type
class Xor(_BinOp):
    pass


@node_type
class Add(_BinOp):
    pass


@node_type
class Sub(_BinOp):
    pass


@node_type
class Mul(_BinOp):
    pass


@node_type
class Div(_BinOp):
    pass


@node_type
class Exp(_BinOp):
    pass


@node_type
class Mod(_BinOp):
    pass


@node_type
class Shr(LLLNode):
    operand: Value
    bits: Value


@node_type
class Shl(LLLNode):
    operand: Value
    bits: Value


@node_type
class Sha3(LLLNode):
    input: Value


@node_type
class Sha3_32(LLLNode):
    input: Value


@node_type
class Sha3_64(LLLNode):
    input: Value
    length: Value


@node_type
class Assert(_UnaryOp):
    pass


@node_type
class CodeLoad(LLLNode):
    length: Value


@node_type
class CodeCopy(LLLNode):
    register: Value
    pointer: Value
    length: Value


@node_type
class CalldataLoad(LLLNode):
    pointer: Value


@node_type
class CalldataCopy(LLLNode):
    register: Value
    pointer: Value
    length: Value


@node_type
class MLoad(LLLNode):
    register: Value


@node_type
class MStore(LLLNode):
    register: Value
    value: Value


@node_type
class SLoad(LLLNode):
    slot: Value


@node_type
class SStore(LLLNode):
    slot: Value
    value: Value


@node_type
class Goto(LLLNode):
    label: Var


@node_type
class Label(LLLNode):
    label: Var


@node_type
class JumpDest(LLLNode):
    pass


@node_type
class Jump(LLLNode):
    offset: Value


@node_type
class Repeat(LLLNode):
    offset: Value


@node_type
class Dup1(LLLNode):
    register: Value


@node_type
class Pop(_UnaryOp):
    pass


@node_type
class Log1(LLLNode):
    register: Value


@node_type
class Log2(LLLNode):
    register: Value


@node_type
class Log3(LLLNode):
    register: Value


@node_type
class Log4(LLLNode):
    register: Value


# Dynamically load all ast classes in this module at runtime
NODES: Dict[str, LLLNode] = {
    node_type.lower(): node
    for node_type, node in inspect.getmembers(sys.modules[__name__], predicate=inspect.isclass)
    if not node_type.startswith("_") and node is not LLLNode
}
