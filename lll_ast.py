from typing import Dict, List, Optional, Union

import inspect
import sys

from node_utils import BaseNode


def _stringify_value(v):
    if isinstance(v, list):
        return " ".join(str(i) for i in v)
    else:
        return str(v)


class LLLNode(BaseNode):
    def __str__(self):
        node_type = self.type.lower()

        if len(list(self)) == 0:
            return node_type

        else:
            attrs = " " + " ".join(_stringify_value(v) for _, v in iter(self))
            return "(" + node_type + attrs + ")"


class Num(LLLNode):
    value: int

    def __str__(self):
        if len(str(self.value)) > 8:
            return hex(self.value)
        else:
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

    def __str__(self):
        gas_limit_str = str(self.gas_limit)
        address_str = str(self.address)
        value_str = str(self.value)
        args_offset_str = str(self.args_offset)
        args_length_str = str(self.args_length)
        return_offset_str = str(self.return_offset)
        return_length_str = str(self.return_length)
        call_str = (
            "(call"
            + " "
            + gas_limit_str
            + " "
            + address_str
            + " "
            + value_str
            + " "
            + args_offset_str
            + " "
            + args_length_str
            + " "
            + return_offset_str
            + " "
            + return_length_str
            + ")"
        )
        if len(call_str) < 80:
            return call_str
        else:
            return (
                "(call"
                + "\n  "
                + gas_limit_str.replace("\n", "\n  ")
                + "\n  "
                + address_str.replace("\n", "\n  ")
                + "\n  "
                + value_str.replace("\n", "\n  ")
                + "\n  "
                + args_offset_str.replace("\n", "\n  ")
                + "\n  "
                + args_length_str.replace("\n", "\n  ")
                + "\n  "
                + return_offset_str.replace("\n", "\n  ")
                + "\n  "
                + return_length_str.replace("\n", "\n  ")
                + ")"
            )


class StaticCall(LLLNode):
    gas_limit: Value
    address: Value
    args_offset: Value
    args_length: Value
    return_offset: Value
    return_length: Value

    def __str__(self):
        gas_limit_str = str(self.gas_limit)
        address_str = str(self.address)
        args_offset_str = str(self.args_offset)
        args_length_str = str(self.args_length)
        return_offset_str = str(self.return_offset)
        return_length_str = str(self.return_length)
        call_str = (
            "(staticcall"
            + " "
            + gas_limit_str
            + " "
            + address_str
            + " "
            + args_offset_str
            + " "
            + args_length_str
            + " "
            + return_offset_str
            + " "
            + return_length_str
            + ")"
        )
        if len(call_str) < 80:
            return call_str
        else:
            return (
                "(staticcall"
                + "\n  "
                + gas_limit_str.replace("\n", "\n  ")
                + "\n  "
                + address_str.replace("\n", "\n  ")
                + "\n  "
                + args_offset_str.replace("\n", "\n  ")
                + "\n  "
                + args_length_str.replace("\n", "\n  ")
                + "\n  "
                + return_offset_str.replace("\n", "\n  ")
                + "\n  "
                + return_length_str.replace("\n", "\n  ")
                + ")"
            )


class Seq(LLLNode):
    statements: List[LLLNode]

    def __str__(self):
        if isinstance(self.statements, list):
            statements = [str(n).replace("\n", "\n  ") for n in self.statements]

        else:
            statements = [str(self.statements).replace("\n", "\n  ")]

        if len(" ".join(statements)) + len(self.type) < 80:
            statements_str = " " + " ".join(statements)

        else:
            statements_str = "\n  " + "\n  ".join(statements)

        return f"({self.type.lower()} {statements_str})"


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

    def __str__(self):
        var_str = str(self.variable)
        val_str = str(self.value)
        stmt_str = str(self.statement)
        with_str = f"(with {var_str} {val_str} {stmt_str})"
        if len(with_str) < 80:
            return with_str
        else:
            return (
                "(with"
                + "\n  "
                + var_str
                + " "
                + val_str.replace("\n", "\n  ")
                + "\n  "
                + stmt_str.replace("\n", "\n  ")
                + ")"
            )


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

    def __str__(self):
        cond_str = str(self.condition)
        true_str = str(self.true)
        false_str = "" if self.false is None else str(self.false)
        if_str = f"(if {cond_str} {true_str} {false_str})"
        if len(if_str) < 80:
            return if_str
        else:
            return (
                "(if"
                + "\n  "
                + cond_str.replace("\n", "\n  ")
                + "\n  "
                + true_str.replace("\n", "\n  ")
                + ("\n  " + false_str.replace("\n", "\n  ") if false_str else "")
                + ")"
            )


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

    def __str__(self):
        val_str = str(self.operand)
        node_type = self.type.lower()
        op_str = f"({node_type} {val_str})"
        if len(op_str) < 80:
            return op_str
        else:
            return "(" + node_type + "\n  " + val_str.replace("\n", "\n  ") + ")"


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

    def __str__(self):
        lhs_str = str(self.lhs)
        rhs_str = str(self.rhs)
        node_type = self.type.lower()
        op_str = f"({node_type} {lhs_str} {rhs_str})"
        if len(op_str) < 80:
            return op_str
        else:
            return (
                "("
                + node_type
                + "\n  "
                + lhs_str.replace("\n", "\n  ")
                + "\n  "
                + rhs_str.replace("\n", "\n  ")
                + ")"
            )


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
