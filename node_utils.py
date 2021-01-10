import dataclasses as dc

from typing import (
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from errors import CompilerError

NodeAttr = Union[List["BaseNode"], "BaseNode"]

node_type = dc.dataclass


@node_type
class BaseNode:
    def iter_attributes(self,) -> Generator[Tuple[str, NodeAttr], None, None]:
        for field in dc.fields(self):
            value = getattr(self, field.name)
            if isinstance(value, (list, BaseNode)):
                yield field.name, value

    @property
    def node_type(self):
        return self.__class__.__name__


NodeClass = Type[BaseNode]
FnType = TypeVar("FnType")
ReturnType = TypeVar("ReturnType")
Context = TypeVar("Context")
VisitFn = Callable[[BaseNode, Optional[Context]], None]
MutateFn = Callable[[BaseNode, Optional[Context]], Union[BaseNode, None]]
TransformFn = Callable[[BaseNode, Optional[Context]], ReturnType]


class BaseVisitor(Generic[FnType, Context]):
    def __init__(self, node_base_class: NodeClass):
        self._functions: Dict[NodeClass, FnType] = {}
        self._node_base_class = node_base_class

    @property
    def node_class_name(self):
        return self._node_base_class.__name__

    def register(self, node_class: NodeClass):
        """
        Decorator that allows registering visitor functions
        """

        def register(function: FnType):
            if node_class in self._functions.keys():
                raise CompilerError(f"'{node_class}' already registered")

            if not issubclass(node_class, self._node_base_class):
                raise CompilerError(
                    f"'{node_class.__name__}' is not a " f"'{self.node_class_name}'"
                )

            else:
                self._functions[node_class] = function

        return register


class NodeVisitor(BaseVisitor[VisitFn, Context]):
    """
    Visitor Generic class:
        visit and view nodes in a tree-like structure of `NodeClass`

        functions must be pure, taking `NodeClass` as input and return nothing
    """

    def visit(self, node: BaseNode, context: Optional[Context] = None):
        node_class = node.__class__

        if not isinstance(node, self._node_base_class):
            raise CompilerError(
                f"`{node_class.__name__}` is not a `{self.node_class_name}`"
            )

        elif node.__class__ in self._functions.keys():
            self._functions[node_class](node, context)

        elif self._node_base_class in self._functions.keys():
            return self._functions[self._node_base_class](node, context)

        else:
            self._generic_visit(node, context)

    def _generic_visit(self, node: BaseNode, context: Optional[Context] = None):
        for attr, value in node.iter_attributes():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, self._node_base_class):
                        self.visit(item, context)

                    else:
                        raise CompilerError(
                            f"Item {item} in '{attr}' of {node} is not of type"
                            f" {self.node_class_name}"
                        )

            elif isinstance(value, self._node_base_class):
                self.visit(value, context)

            else:
                raise CompilerError(
                    f"'{attr}' of {node} is not a list or {self.node_class_name}"
                )


class NodeMutator(BaseVisitor[MutateFn, Context]):
    """
    Mutating Visitor Generic class:
        visit and modify nodes in a tree-like structure of `NodeClass`

        functions must be pure, taking `NodeClass` as input
        and return it with any necessary modifications
    """

    def update(
        self, node: BaseNode, context: Optional[Context] = None
    ) -> Union[BaseNode, None]:
        node_class = node.__class__

        if not isinstance(node, self._node_base_class):
            raise CompilerError(
                f"`{node_class.__name__}` is not a `{self.node_class_name}`"
            )

        elif node.__class__ in self._functions.keys():
            return self._functions[node_class](node, context)

        elif self._node_base_class in self._functions.keys():
            return self._functions[self._node_base_class](node, context)

        else:
            return self._generic_visit(node, context)

    def _generic_visit(
        self, node: BaseNode, context: Optional[Context] = None
    ) -> Union[BaseNode, None]:
        for attr, old_value in node.iter_attributes():
            if isinstance(old_value, list):
                new_values: List[BaseNode] = []
                for old_item in old_value:
                    if isinstance(old_item, self._node_base_class):
                        new_item = self.update(old_item, context)

                        if new_item is None:
                            continue  # pruned node

                        elif isinstance(new_item, self._node_base_class):
                            new_values.append(new_item)

                        else:
                            raise CompilerError(
                                f"Updated item {new_item} of '{attr}' in "
                                f"{node} is not of type {self.node_class_name}"
                            )

                    else:
                        raise CompilerError(
                            f"Item {old_item} in '{attr}' of {node} is not of"
                            f" type {self.node_class_name}"
                        )

                setattr(node, attr, new_values)

            elif isinstance(old_value, self._node_base_class):
                new_value = self.update(old_value, context)

                if new_value is None:
                    delattr(node, attr)  # pruned node

                elif isinstance(new_value, self._node_base_class):
                    setattr(node, attr, new_value)

                else:
                    raise CompilerError(
                        f"Updated '{attr}' {new_value} in {node}"
                        f" is not of type {self.node_class_name}"
                    )

            else:
                raise CompilerError(
                    f"'{attr}' of {node} is not a list or {self.node_class_name}"
                )

        return node


class NodeTransformer(
    BaseVisitor[TransformFn, Context], Generic[FnType, ReturnType, Context]
):
    """
    Transformer Generic class:
        visit and transform nodes in a tree-like structure of `NodeClass`

        functions must be pure, with `NodeClass` as input and `ReturnType` as output

        There is no default (all nodes in tree must have transforms)
    """

    def transform(
        self, node: BaseNode, context: Optional[Context] = None
    ) -> ReturnType:
        node_class = node.__class__

        if not isinstance(node, self._node_base_class):
            raise CompilerError(
                f"`{node_class.__name__}` is not a `{self.node_class_name}`"
            )

        elif node.__class__ in self._functions.keys():
            return self._functions[node_class](node, context)

        elif self._node_base_class in self._functions.keys():
            return self._functions[self._node_base_class](node, context)

        else:
            raise CompilerError(f"Transform for '{node.__class__}' is not registered")
