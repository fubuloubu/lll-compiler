from typing import Dict, Tuple

import inspect
import sys


class LLLNode:
    attrs: Tuple = ()
    # NOTE: Cannot use both optional and unbounded
    optional: Tuple = ()
    unbounded: bool = False

    @property
    def node_type(self):
        return self.__class__.__name__.lower()

    def __init__(self, *args):
        if not self.unbounded and (
            # Less than the number of required args
            len(self.attrs) < len(args)
            # Greater than the number of total args
            or len(args) > len(self.attrs) + len(self.optional)
        ):
            raise TypeError(f"Wrong args for '{repr(self)}': {args}")

        for attr, value in zip(self.attrs + self.optional, args):
            setattr(self, attr, value)

        if self.unbounded:
            setattr(
                self,
                self.attrs[-1],
                # Add the rest of the arguments
                tuple([getattr(self, self.attrs[-1])] + list(args[len(self.attrs) :])),
            )

    def __repr__(self):
        args = " ".join(
            ["~" + a for a in self.attrs]  # ~arg
            + ["[" + a + "]" for a in self.optional]  # [optional]
        )
        return (
            f"({self.node_type} {args})"
            if len(args) > 1  # Will be empty string if no req'd or opt args
            else self.node_type  # NullOp
        )

    def __str__(self):
        attrs = [str(getattr(self, attr)) for attr in self.attrs]
        for attr in self.optional:
            if hasattr(self, attr):
                attrs.append(getattr(self, attr))
        return (
            f"({self.node_type} {' '.join(attrs)})"
            if len(self.attrs) > 1
            else self.node_type
        )


class Call(LLLNode):
    attrs = (
        "gas_limit",
        "address",
        "value",
        "args_offset",
        "args_length",
        "return_offset",
        "return_length",
    )


class Seq(LLLNode):
    attrs = ("statements",)
    unbounded = True


class Seq_Unchecked(LLLNode):
    attrs = ("statements",)
    unbounded = True


class With(LLLNode):
    attrs = ("name", "value", "statement")


class If(LLLNode):
    attrs = ("condition", "positive")
    optional = ("negative",)


class _NullOp(LLLNode):
    pass


class Caller(_NullOp):
    pass


class Pass(_NullOp):
    pass


class Stop(_NullOp):
    pass


class Gas(_NullOp):
    pass


class CodeSize(_NullOp):
    pass


class CalldataSize(_NullOp):
    pass


class ReturndataSize(_NullOp):
    pass


class _UnaryOp(LLLNode):
    attrs = ("input",)


class Not(_UnaryOp):
    pass


class IsZero(_UnaryOp):
    pass


class _BinOp(LLLNode):
    attrs = ("lhs", "rhs")


class Eq(_BinOp):
    pass


class Ne(_BinOp):
    pass


class Ge(_BinOp):
    pass


class Gt(_BinOp):
    pass


class Le(_BinOp):
    pass


class Lt(_BinOp):
    pass


class Slt(_BinOp):
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


class Shr(LLLNode):
    attrs = ("operand", "bits")


class Shl(LLLNode):
    attrs = ("operand", "bits")


class Sha3_64(LLLNode):
    attrs = ("slot", "value")


class Assert(LLLNode):
    attrs = ("condition",)


class CodeLoad(LLLNode):
    attrs = ("length",)


class CodeCopy(LLLNode):
    attrs = ("register", "pointer", "length")


class CalldataLoad(LLLNode):
    attrs = ("pointer",)


class CalldataCopy(LLLNode):
    attrs = ("register", "pointer", "length")


class MLoad(LLLNode):
    attrs = ("register",)


class MStore(LLLNode):
    attrs = ("register", "value")


class SLoad(LLLNode):
    attrs = ("slot",)


class SStore(LLLNode):
    attrs = ("slot", "value")


class Goto(LLLNode):
    attrs = ("label",)


class Label(LLLNode):
    attrs = ("name",)


class JumpDest(_NullOp):
    pass


class Jump(LLLNode):
    attrs = ("offset",)


class Dup1(LLLNode):
    attrs = ("register",)


class Pop(_UnaryOp):
    pass


# Dynamically load all ast classes in this module at runtime
NODES: Dict[str, LLLNode] = {
    node_type.lower(): node
    for node_type, node in inspect.getmembers(
        sys.modules[__name__], predicate=inspect.isclass
    )
    if not node_type.startswith("_") and node is not LLLNode
}
