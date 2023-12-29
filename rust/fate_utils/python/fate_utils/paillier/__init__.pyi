from typing import Any, List, Tuple, Union, Optional
import numpy as np
from numpy import ndarray as Array

class PK:
    def __init__(self) -> None: ...
    def encrypt_encoded(self, fixedpoint: FixedpointVector, obfuscate: bool) -> FixedpointPaillierVector: ...
    def encrypt_encoded_scalar(self, fixedpoint: FixedpointEncoded, obfuscate: bool) -> PyCT: ...
    def __new__(self) -> "PK": ...
    def __getstate__(self) -> List[bytes]: ...
    def __setstate__(self, state: List[bytes]) -> None: ...

class SK:
    def __init__(self) -> None: ...
    def decrypt_to_encoded(self, data: FixedpointPaillierVector) -> FixedpointVector: ...
    def decrypt_to_encoded_scalar(self, data: PyCT) -> FixedpointEncoded: ...
    def __new__(self) -> "SK": ...
    def __getstate__(self) -> List[bytes]: ...
    def __setstate__(self, state: List[bytes]) -> None: ...

class Coders:
    def __init__(self) -> None: ...
    def encode_f64(self, data: float) -> FixedpointEncoded: ...
    def encode_f64_vec(self, data: Array[float]) -> FixedpointVector: ...
    def decode_f64(self, data: FixedpointEncoded) -> float: ...
    def decode_f64_vec(self, data: FixedpointVector) -> Array[float]: ...
    def encode_f32(self, data: float) -> FixedpointEncoded: ...
    def encode_f32_vec(self, data: Array[float]) -> FixedpointVector: ...
    def decode_f32(self, data: FixedpointEncoded) -> float: ...
    def decode_f32_vec(self, data: FixedpointVector) -> Array[float]: ...
    def encode_i64(self, data: int) -> FixedpointEncoded: ...
    def encode_i64_vec(self, data: Array[int]) -> FixedpointVector: ...
    def decode_i64(self, data: FixedpointEncoded) -> int: ...
    def decode_i64_vec(self, data: FixedpointVector) -> List[int]: ...
    def encode_i32(self, data: int) -> FixedpointEncoded: ...
    def encode_i32_vec(self, data: Array[int]) -> FixedpointVector: ...
    def decode_i32(self, data: FixedpointEncoded) -> int: ...
    def decode_i32_vec(self, data: FixedpointVector) -> List[int]: ...
    def __getstate__(self) -> List[bytes]: ...
    def __setstate__(self, state: List[bytes]) -> None: ...

class FixedpointPaillierVector:
    def __init__(self) -> None: ...
    def zeros(self, size: int) -> "FixedpointPaillierVector": ...
    # Other methods...

class FixedpointVector:
    def __init__(self) -> None: ...
    # Other methods...

class PyCT:
    ct: Any

class FixedpointEncoded:
    data: Any

def keygen(bit_length: int) -> Tuple[SK, PK, Coders]: ...
