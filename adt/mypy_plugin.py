from typing import Optional, Callable, List, Type, Any, Iterable, Union
import typing
import mypy.types
from mypy.plugin import AnalyzeTypeContext, TypeAnalyzerPluginInterface, ClassDefContext, Plugin, ClassDef
# from mypy.plugins.common import add_method
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
from mypy.semanal import set_callable_name
from mypy.typevars import fill_typevars
from mypy.util import get_unique_redefinition_name


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
    cls = context.cls
    # print(context)
    print(context.cls)
    # context.cls.base_type_exprs.append(NameExpr("int"))
    # print(context.api.named_type('typing.Union[int, str]'))

    # add_method(
    #     ctx=context,
    #     name="__new__",
    #     args=[],
    #     return_type=mypy.types.NoneType(),
    #     self_type=None,
    #     tvar_def=None,
    #     is_classmethod=True,
    # )
    #

    print([x.name for x in context.cls.base_type_exprs])

    print(context.cls)

    # cases = get_and_delete_cases(context)
    #
    # print(type(cases[1][0]), type(cases[1][1]))
    # print(cases[1][1])
    # cls.info._promote = [mypy.types.AnyType(2)]
    #
    # print(cls.info._promote)
    # cls.info.bases = []
    # print(cls.info.bases)


def get_and_delete_cases(context: ClassDefContext):
    cls = context.cls
    cases = []
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

        cases.append((lval.name, var.type))

    return cases


class CaseDefs:
    context: ClassDefContext
    name: str
    types: List[mypy.types.Type]


# fullname and name became properties with https://github.com/python/mypy/pull/7829
# These are compatibility shims
def get_fullname(x: Union[FuncBase, SymbolNode]) -> str:
    fn = x.fullname
    if callable(fn):
        return typing.cast(str, fn())
    return typing.cast(str, fn)


def get_name(x: Union[FuncBase, SymbolNode]) -> str:
    fn = x.name
    if callable(fn):
        return typing.cast(str, fn())
    return fn


def add_method(
        ctx: ClassDefContext,
        name: str,
        args: List[Argument],
        return_type: mypy.types.Type,
        self_type: Optional[mypy.types.Type] = None,
        tvar_def: Optional[mypy.types.TypeVarType] = None,
        is_classmethod: bool = False,
) -> None:
    """Adds a new method to a class.
    """
    info = ctx.cls.info

    # First remove any previously generated methods with the same name
    # to avoid clashes and problems in new semantic analyzer.
    if name in info.names:
        sym = info.names[name]
        if sym.plugin_generated and isinstance(sym.node, FuncDef):
            ctx.cls.defs.body.remove(sym.node)

    if is_classmethod:
        first = Argument(
            Var('cls'),
            # Working around python/mypy#5416.
            # This should be: mypy.types.TypeType.make_normalized(self_type)
            mypy.types.AnyType(mypy.types.TypeOfAny.implementation_artifact),
            None,
            ARG_POS)
    else:
        self_type = self_type or fill_typevars(info)
        first = Argument(Var('self'), self_type, None, ARG_POS)

    args = [first] + args

    function_type = ctx.api.named_type('__builtins__.function')

    arg_types, arg_names, arg_kinds = [], [], []
    for arg in args:
        assert arg.type_annotation, 'All arguments must be fully typed.'
        arg_types.append(arg.type_annotation)
        arg_names.append(get_name(arg.variable))
        arg_kinds.append(arg.kind)

    signature = mypy.types.CallableType(arg_types, arg_kinds, arg_names,
                                        return_type, function_type)
    if tvar_def:
        signature.variables = [tvar_def]

    func = FuncDef(name, args, Block([PassStmt()]))
    func.info = info
    func.is_class = is_classmethod
    func.type = set_callable_name(signature, func)
    func._fullname = get_fullname(info) + '.' + name
    func.line = info.line

    # NOTE: we would like the plugin generated node to dominate, but we still
    # need to keep any existing definitions so they get semantically analyzed.
    if name in info.names:
        # Get a nice unique name instead.
        r_name = get_unique_redefinition_name(name, info.names)
        info.names[r_name] = info.names[name]

    info.defn.defs.body.append(func)
    info.names[name] = SymbolTableNode(MDEF, func, plugin_generated=True)

