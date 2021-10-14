from typing import Optional, Callable, List, Type, Any, Iterable, Union
import mypy.types
from mypy.plugin import AnalyzeTypeContext, TypeAnalyzerPluginInterface, ClassDefContext, Plugin, ClassDef
from mypy.nodes import (
    ARG_NAMED,
    ARG_POS,
    MDEF,
    Argument,
    AssignmentStmt,
    Block,
    FuncDef,
    FuncBase,
    NameExpr,
    PassStmt,
    PlaceholderNode,
    SymbolTableNode,
    SymbolNode,
    TypeVarExpr,
    Var,
)


def plugin(version: str) -> Type[Plugin]:
    """Return plugin class depending on mypy version."""
    return ADTPlugin


class ADTPlugin(Plugin):
    ADT_META_CLASS_NAME = "adt.adt.ADTMeta"

    def get_metaclass_hook(self, fullname: str
                           ) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname == self.ADT_META_CLASS_NAME:
            return adt_meta_transform
        return None


def adt_meta_transform(context: ClassDefContext):
    print(context)
    print(context.cls)

    get_and_delete_cases(context)


def get_and_delete_cases(context: ClassDefContext):
    cls = context.cls
    for statement in cls.defs.body:
        # Any assignment that doesn't use the new type declaration
        # syntax can be ignored out of hand.
        if not (isinstance(statement, AssignmentStmt)
                and statement.new_syntax):
            continue

        # a: int, b: str = 1, 'foo' is not supported syntax so we
        # don't have to worry about it.
        lval = statement.lvalues[0]
        if not isinstance(lval, NameExpr):
            continue

        sym = cls.info.names.get(lval.name)
        if sym is None:
            # This name is likely blocked by a star import. We don't need to defer because
            # defer() is already called by mark_incomplete().
            continue

        var = sym.node
        if isinstance(var, PlaceholderNode):
            # This node is not ready yet.
            return None

        print("Case: ", sym)
        print(var)

class CaseDefs:
    context: ClassDefContext
    name: str
    types: List[mypy.types.Type]


