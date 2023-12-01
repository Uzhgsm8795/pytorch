import contextlib
from enum import IntEnum

import torch

__all__ = [
    "ATFPBackend",
    "atfp_kernel",
    "atfp_math_enabled",
    "enable_atfp_math",
    "atfp_mha_enabled",
    "enable_atfp_mha",
    "atfp_encoder_enabled",
    "enable_atfp_encoder",
    "atfp_nested_tensor_enabled",
    "enable_atfp_nested_tensor",
]


class ATFPBackend(IntEnum):
    r"""Enum class for the AT Inference Fastpath backends.

    .. warning:: This class is in beta and subject to change.
    """
    ERROR = -1
    MATH = 0
    MHA = 1
    ENCODER = 2
    NESTED_TENSOR = 3
    bits = 4


def _write_global_ctx(ctx_no: int, enabled: bool, default: bool = True) -> None:
    r"""
    .. warning:: This flag is beta and subject to change.

    Enables or disables global ctx represented by `ctx_no`.
    """
    # default (represented by global ctx value of 0/False) for ATFP backend feature enablement is true
    # so ctx bit being set disables the feature, and we need to invert the boolean "enabled"
    if enabled == default:
        if not torch.jit.is_scripting():
            torch._C._unset_global_ctx(ctx_no)
        else:
            torch.ops.prim._UnsetGlobalCtx(ctx_no)
    else:
        if not torch.jit.is_scripting():
            torch._C._set_global_ctx(ctx_no)
        else:
            torch.ops.prim._SetGlobalCtx(ctx_no)


def _is_global_ctx(ctx_no: int, default: bool = True) -> bool:
    r"""
    .. warning:: This flag is beta and subject to change.

    Returns whether global ctx `ctx_no` is enabled or disabled.
    """
    # default (represented by global ctx value of 0/False) for ATFP backend feature enablement is true
    # so ctx bit being set disables the feature, and we need to invert the boolean "enabled"
    if not torch.jit.is_scripting():
        return torch._C._get_global_ctx(ctx_no) != default
    else:
        return torch.ops.prim._GetGlobalCtx(ctx_no) != default


def atfp_math_enabled() -> bool:
    r"""
    .. warning:: This flag is beta and subject to change.

    Returns whether math kernel for AT Inference Fastpath is enabled or not.
    """
    return _is_global_ctx(0)  # ATFPBackend.MATH


def enable_atfp_math(enabled: bool) -> None:
    r"""
    .. warning:: This flag is beta and subject to change.

    Enables or disables math kernel for AT Inference Fastpath.
    """
    _write_global_ctx(0, enabled)  # ATFPBackend.MATH


def atfp_mha_enabled() -> bool:
    r"""
    .. warning:: This flag is beta and subject to change.

    Returns whether MHA kernel for AT Inference Fastpath is enabled or not.
    """
    return _is_global_ctx(1)  # ATFPBackend.MHA


def enable_atfp_mha(enabled: bool) -> None:
    r"""
    .. warning:: This flag is beta and subject to change.

    Enables or disables MHA kernel for AT Inference Fastpath.
    """
    _write_global_ctx(1, enabled)  # ATFPBackend.MATH


def atfp_encoder_enabled() -> bool:
    r"""
    .. warning:: This flag is beta and subject to change.

    Returns whether encoder kernel for AT Inference Fastpath is enabled or not.
    """
    return _is_global_ctx(2)  # ATFPBackend.ENCODER


def enable_atfp_encoder(enabled: bool) -> None:
    r"""
    .. warning:: This flag is beta and subject to change.

    Enables or disables encoder kernel for AT Inference Fastpath.
    """
    _write_global_ctx(2, enabled)  # ATFPBackend.ENCODER


def atfp_nested_tensor_enabled() -> bool:
    r"""
    .. warning:: This flag is beta and subject to change.

    Returns whether nested_tensor kernel for AT Inference Fastpath is enabled or not.
    """
    return _is_global_ctx(3)  # ATFPBackend.NESTED_TENSOR


def enable_atfp_nested_tensor(enabled: bool) -> None:
    r"""
    .. warning:: This flag is beta and subject to change.

    Enables or disables nested_tensor kernel for AT Inference Fastpath.
    """
    _write_global_ctx(3, enabled)  # ATFPBackend.NESTED_TENSOR


@contextlib.contextmanager
def atfp_kernel(
    *,
    enable_nested_tensor: bool = True,
    enable_encoder: bool = True,
    enable_mha: bool = True,
    enable_math: bool = True,
):
    r"""
    .. warning:: This flag is beta and subject to change.

    This context manager can be used to temporarily enable or disable any of the four backends for
    Accelerated Transformer Inference Fastpath.
    Upon exiting the context manager, the previous state of the flags will be restored.
    """
    previous_math: bool = atfp_math_enabled()
    previous_mha: bool = atfp_mha_enabled()
    previous_encoder: bool = atfp_encoder_enabled()
    previous_nested_tensor: bool = atfp_nested_tensor_enabled()
    try:
        enable_atfp_math(enable_math)
        enable_atfp_mha(enable_mha)
        enable_atfp_encoder(enable_encoder)
        enable_atfp_nested_tensor(enable_nested_tensor)
        yield {}
    finally:
        enable_atfp_math(previous_math)
        enable_atfp_mha(previous_mha)
        enable_atfp_encoder(previous_encoder)
        enable_atfp_nested_tensor(previous_nested_tensor)
