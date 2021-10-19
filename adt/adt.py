from typing import cast


class ADTMeta(type):
    def __new__(mcs, name, bases, namespace: dict):
        module = namespace["__module__"]
        adt_qualname = namespace["__qualname__"]

        annotations = namespace.pop("__annotations__", {})
        variants = {}
        for variant_name, variant_annotation in annotations.items():
            variant_class = type(variant_name, (), {
                "__module__": module,
                "__qualname__": f"{adt_qualname}.{variant_name}",
            })
            variants[variant_name] = variant_class

        adt_class = type(name, bases, {
            "__module__": module,
            "__qualname__": adt_qualname,
            "__annotations__": variants,
            **variants
        })

        # ADTGenericAlias = type(f"{name}Type", (_UnionGenericAlias,), {
        #     "__repr__": lambda self: f"{self.__module__}.{self.__qualname__}[{', '.join([arg.__name__ for arg in self.__args__])}]",
        #     "__annotations__": variants,
        #     **variants
        # }, _root=True)
        #
        # a = ADTGenericAlias(adt_class, tuple(variants.values()))

        return cast(adt_class, adt_class)
