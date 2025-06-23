import builtins
import sys
import hashlib

from typing import Optional, Union, Callable, List

bytes_ = builtins.bytes  # alias the stdlib type but ew


def unicode(text: Union[bytes_, str]) -> str:
    if not isinstance(text, str):
        return text.decode('utf-8')
    else:
        return text


def bytes(text: Optional[Union[str, bytes_]]) -> bytes_:
    """
    Convert Unicode text to UTF-8 encoded bytes.

    Since Python 2.6+ and Python 3+ have similar but incompatible
    signatures, this function unifies the two to keep code sane.

    :param text: Unicode text to convert to bytes
    :rtype: bytes (Python3), str (Python2.6+)
    """
    if text is None:
        return b''

    if isinstance(text, builtins.bytes):
        # We already have bytes, so do nothing
        return text
    if isinstance(text, list):
        # Convert a list of integers to bytes
        return builtins.bytes(text)
    else:
        # Convert UTF-8 text to bytes
        return builtins.bytes(text, encoding='utf-8')


def quote(text: Union[str, bytes_]) -> bytes_:
    """
    Enclose in quotes and escape internal slashes and double quotes.

    :param text: A Unicode or byte string.
    """
    text = bytes(text)
    return b'"' + text.replace(b'\\', b'\\\\').replace(b'"', b'\\"') + b'"'


def num_to_bytes(num: int) -> bytes_:
    """
    Convert an integer into a four byte sequence.

    :param integer num: An integer to convert to its byte representation.
    """
    bval = b''
    bval += bytes(chr(0xFF & (num >> 24)))
    bval += bytes(chr(0xFF & (num >> 16)))
    bval += bytes(chr(0xFF & (num >> 8)))
    bval += bytes(chr(0xFF & (num >> 0)))
    return bval


def bytes_to_num(bval: bytes_) -> int:
    """
    Convert a four byte sequence to an integer.

    :param bytes bval: A four byte sequence to turn into an integer.
    """
    num = 0
    num += (bval[0] << 24)
    num += (bval[1] << 16)
    num += (bval[2] << 8)
    num += (bval[3])
    return num


def XOR(x: bytes_, y: bytes_) -> bytes_:
    """
    Return the results of an XOR operation on two equal length byte strings.

    :param bytes x: A byte string
    :param bytes y: A byte string
    :rtype: bytes
    """
    # This operation is faster with a list comprehension than with a
    # generator, as of 2016 on python 3.5.
    return builtins.bytes([a ^ b for a, b in zip(x, y)])


def hash(name: str) -> Optional[Callable]:
    """
    Return a hash function implementing the given algorithm.

    :param name: The name of the hashing algorithm to use.
    :type name: string

    :rtype: function
    """
    name = name.lower()
    if name.startswith('sha-'):
        name = 'sha' + name[4:]
    if name in dir(hashlib):
        return getattr(hashlib, name)
    return None


def hashes() -> List[str]:
    """
    Return a list of available hashing algorithms.

    :rtype: list of strings
    """
    t = []
    if 'md5' in dir(hashlib):
        t = ['MD5']
    if 'md2' in dir(hashlib):
        t += ['MD2']
    hashes = ['SHA-' + h[3:] for h in dir(hashlib) if h.startswith('sha')]
    return t + hashes
