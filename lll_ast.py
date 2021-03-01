from typing import Dict, List, Optional, Union

import inspect
import sys

from node_utils import BaseNode


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


class Num(LLLNode):
    value: int

    def __str__(self):
        return str(self.value)


class Var(LLLNode):
    name: str

    def __str__(self):
        return self.name


Value = Union[Num, Var, LLLNode]


class Call(LLLNode):
    gas_limit: Value
    address: Value
    value: Value
    args_offset: Value
    args_length: Value
    return_offset: Value
    return_length: Value


class StaticCall(LLLNode):
    gas_limit: Value
    address: Value
    args_offset: Value
    args_length: Value
    return_offset: Value
    return_length: Value



class Seq(LLLNode):
    statements: List[LLLNode]


# NOTE: This node is sometimes present, it's an alias
# TODO: Delete this node
class Set(Seq):
    pass


# NOTE: This node is sometimes present, it's an alias
# TODO: Delete this node
class Lll(Seq):
    pass


# NOTE: This node is sometimes present, it's an alias
# TODO: Delete this node
class Seq_Unchecked(Seq):
    pass


class With(LLLNode):
    variable: Var
    value: Value
    statement: Value


class Return(LLLNode):
    pointer: Value
    length: Value


class Revert(LLLNode):
    pointer: Value
    length: Value


class If(LLLNode):
    condition: Value
    true: Value
    false: Optional[Value] = None


class Caller(LLLNode):
    pass


class Pass(LLLNode):
    pass


class Stop(LLLNode):
    pass


class Gas(LLLNode):
    pass


class CodeSize(LLLNode):
    pass


class CalldataSize(LLLNode):
    pass


class ReturndataSize(LLLNode):
    pass


class _UnaryOp(LLLNode):
    operand: Value


class Not(_UnaryOp):
    pass


class Clamp_NonZero(_UnaryOp):
    pass


class IsZero(_UnaryOp):
    pass


class Ceil32(_UnaryOp):
    pass


class ExtCodeSize(_UnaryOp):
    pass


class ExtCodeHash(_UnaryOp):
    pass


class SelfDestruct(_UnaryOp):
    pass


class _BinOp(LLLNode):
    lhs: Value
    rhs: Value


class Eq(_BinOp):
    pass


class Ne(_BinOp):
    pass


class Ge(_BinOp):
    pass


class Sge(_BinOp):
    pass


class Gt(_BinOp):
    pass


class Le(_BinOp):
    pass


class Lt(_BinOp):
    pass


class Slt(_BinOp):
    pass


class Sgt(_BinOp):
    pass


class UClampLt(_BinOp):
    pass


class Or(_BinOp):
    pass


class And(_BinOp):
    pass


class Xor(_BinOp):
    pass


class Add(_BinOp):
    pass


class Sub(_BinOp):
    pass


class Mul(_BinOp):
    pass


class Div(_BinOp):
    pass


class Exp(_BinOp):
    pass


class Mod(_BinOp):
    pass


class Shr(LLLNode):
    operand: Value
    bits: Value


class Shl(LLLNode):
    operand: Value
    bits: Value


class Sha3(LLLNode):
    input: Value


class Sha3_32(LLLNode):
    input: Value


class Sha3_64(LLLNode):
    input: Value
    length: Value


class Assert(_UnaryOp):
    pass


class CodeLoad(LLLNode):
    length: Value


class CodeCopy(LLLNode):
    register: Value
    pointer: Value
    length: Value


class CalldataLoad(LLLNode):
    pointer: Value


class CalldataCopy(LLLNode):
    register: Value
    pointer: Value
    length: Value


class MLoad(LLLNode):
    register: Value


class MStore(LLLNode):
    register: Value
    value: Value


class SLoad(LLLNode):
    slot: Value


class SStore(LLLNode):
    slot: Value
    value: Value


class Goto(LLLNode):
    label: Var


class Label(LLLNode):
    label: Var


class JumpDest(LLLNode):
    pass


class Jump(LLLNode):
    offset: Value


class Repeat(LLLNode):
    offset: Value


class Dup1(LLLNode):
    register: Value


class Pop(_UnaryOp):
    pass


class Log1(LLLNode):
    register: Value


class Log2(LLLNode):
    register: Value


class Log3(LLLNode):
    register: Value


class Log4(LLLNode):
    register: Value


# Dynamically load all ast classes in this module at runtime
NODES: Dict[str, LLLNode] = {
    node_type.lower(): node
    for node_type, node in inspect.getmembers(sys.modules[__name__], predicate=inspect.isclass)
    if not node_type.startswith("_") and node is not LLLNode
}
