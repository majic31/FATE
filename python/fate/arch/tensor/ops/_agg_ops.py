from typing import overload

from .._tensor import Tensor

# TODO: parameter `keepdim` maybe a bit complex in distributed version, fix me later


@overload
def sum(a: Tensor, *, dtype=None) -> Tensor:
    ...


@overload
def sum(a: Tensor, dim, keepdim=False, *, dtype=None) -> Tensor:
    ...


def sum(a: Tensor, *args, **kwargs):
    storage = a.storage
    if func := getattr(storage, "sum"):
        return Tensor(func(*args, **kwargs))
    else:
        raise NotImplementedError(f"sum not impl for tensor `{a}` with storage `{storage}`")


def mean(a: Tensor, *args, **kwargs):
    storage = a.storage
    if func := getattr(storage, "mean"):
        return Tensor(func(*args, **kwargs))
    else:
        raise NotImplementedError(f"mean not impl for tensor `{a}` with storage `{storage}`")


def std(a: Tensor, *args, **kwargs):
    storage = a.storage
    if func := getattr(storage, "std"):
        return Tensor(func(*args, **kwargs))
    else:
        raise NotImplementedError(f"std not impl for tensor `{a}` with storage `{storage}`")


def var(a: Tensor, *args, **kwargs):
    storage = a.storage
    if func := getattr(storage, "var"):
        return Tensor(func(*args, **kwargs))
    else:
        raise NotImplementedError(f"var not impl for tensor `{a}` with storage `{storage}`")


def max(a: Tensor, *args, **kwargs):
    storage = a.storage
    if func := getattr(storage, "max"):
        return Tensor(func(*args, **kwargs))
    else:
        raise NotImplementedError(f"max not impl for tensor `{a}` with storage `{storage}`")


def min(a: Tensor, *args, **kwargs):
    storage = a.storage
    if func := getattr(storage, "min"):
        return Tensor(func(*args, **kwargs))
    else:
        raise NotImplementedError(f"min not impl for tensor `{a}` with storage `{storage}`")