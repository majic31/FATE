from typing import Dict, TypeVar

import pydantic


class ParameterDescribe:
    def __init__(self, name, type, default, optional, desc) -> None:
        self.name = name
        self.type = type
        self.default = default
        self.optional = optional
        self.desc = desc

    def __str__(self) -> str:
        return f"Parameter<name={self.name}, type={self.type}, default={self.default}, optional={self.optional}>"

    def merge(self, p: "ParameterDescribe"):
        if self.default != p.default:
            raise ComponentParameterDuplicateError(
                f"parameter {p.name} declare multiple times with different default: `{self.default}` vs `{p.default}`"
            )
        if self.optional != p.optional:
            raise ComponentParameterDuplicateError(
                f"parameter {p.name} declare multiple times with different optional: `{self.optional}` vs `{p.optional}`"
            )
        if self.type != p.type:
            raise ComponentParameterDuplicateError(
                f"parameter {p.name} declare multiple times with different type: `{self.type}` vs `{self.type}`"
            )
        return self

    def get_parameter_spec(self):
        from fate.components.core.params import Parameter
        from fate.components.core.spec.component import ParameterSpec

        if isinstance(self.type, Parameter):  # recomanded
            type_name = type(self.type).__name__
            type_meta = self.type.dict()
        else:
            field_default = ... if self.default is None else self.default
            parameter_type = pydantic.create_model(f"parameter_{self.name}", data=(self.type, field_default))
            type_name = parameter_type.__name__
            type_meta = parameter_type.schema()

        return ParameterSpec(
            type=type_name,
            type_meta=type_meta,
            default=self.default,
            optional=self.optional,
            description=self.desc,
        )

    def apply(self, parameter_config):
        from fate.components.core import params

        if parameter_config is not None:
            try:
                return params.parse(self.type, parameter_config)
            except Exception as e:
                raise ComponentParameterApplyError(
                    f"apply value `{parameter_config}` to parameter `{self.name}` failed: {e}"
                ) from e
        else:
            if not self.optional:
                raise ComponentParameterApplyError(f"parameter `{self.name}` required, declare: `{parameter_config}`")
            else:
                return self.default


class ComponentParameterDescribes:
    def __init__(self, mapping: Dict[str, ParameterDescribe] = None) -> None:
        self.mapping = mapping or {}

    def add_parameter(self, name, type, default, optional, desc):
        if name in self.mapping:
            raise ComponentParameterDuplicateError(f"parameter {name} declare multiple times")
        self.mapping[name] = ParameterDescribe(name, type, default, optional, desc)

    def merge(self, pd: "ComponentParameterDescribes"):
        parameter_mapping = self.mapping.copy()
        for name, p in pd.mapping.items():
            if name not in parameter_mapping:
                parameter_mapping[name] = p
            else:
                parameter_mapping[name].merge(p)
        return ComponentParameterDescribes(parameter_mapping)

    def get_parameters_spec(self):
        return {name: p.get_parameter_spec() for name, p in self.mapping.items()}


class ParameterDescribeAnnotation:
    def __init__(self, type, default, optional, desc) -> None:
        self.type = type
        self.default = default
        self.optional = optional
        self.desc = desc


T = TypeVar("T")


def parameter(type: T, default=None, optional=True, desc="") -> T:
    return ParameterDescribeAnnotation(type, default, optional, desc)


class ComponentParameterApplyError(RuntimeError):
    ...


class ComponentParameterDuplicateError(RuntimeError):
    ...