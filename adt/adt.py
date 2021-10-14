from typing import _UnionGenericAlias


class ADTMeta(type):
    def __new__(mcs, name, bases, namespace: dict):
        adt_class = type(name, bases, namespace)

        annotations = namespace.pop("__annotations__", {})
        variants = {}
        for variant_name, variant_annotation in annotations.items():
            variant_class = type(variant_name, (), {
                "__qualname__": f"{adt_class.__qualname__}.{variant_name}",
            })
            variants[variant_name] = variant_class

        ADTGenericAlias = type(f"{name}Type", (_UnionGenericAlias,), {
            "__repr__": lambda self: f"{self.__module__}.{self.__qualname__}[{', '.join([arg.__name__ for arg in self.__args__])}]",
            "__annotations__": variants,
            **variants
        }, _root=True)

        a = ADTGenericAlias(adt_class, tuple(variants.values()))
        return a
