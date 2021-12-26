"""bencode parser.
A module for encoding and decoding bencode files
https://en.wikipedia.org/wiki/Bencode
"""
from typing import Union

import pytest

TypeEncodable = Union[str, int, list, dict, bytes]

ENCODING = "utf-8"
INTEGER = b"i"
LIST = b"l"
DICT = b"d"
END = b"e"
COLON = b":"


class BencodeDecodeError(Exception):
    """Error during decode."""


class BencodeEncodeError(Exception):
    """Error during encode."""


def _encode_bool(value: bool) -> bytes:
    """Encode a bool object into bencode.

    :param value: The value to encode
    :return: The value encoded in bencode
    """
    return _encode_int(int(value))


def _encode_bytes(value: bytes) -> bytes:
    """Encode a bytes object into bencode.

    :param value: The value to encode
    :return: The value encoded in bencode
    """
    length = str(len(value)).encode(ENCODING)
    return length + COLON + value


def _encode_dict(value: dict[str, TypeEncodable]) -> bytes:
    """Encode a dict object into bencode.

    :param value: The value to encode
    :return: The value encoded in bencode
    """
    sorted_dict = dict(sorted(value.items()))
    result = [DICT]
    for key, item in sorted_dict.items():
        result.append(encode(key))
        result.append(encode(item))
    result.append(END)
    return b"".join(result)


def _encode_int(value: int) -> bytes:
    """Encode an int object into bencode.

    :param value: The value to encode
    :return: The value encoded in bencode
    """
    return INTEGER + str(value).encode(ENCODING) + END


def _encode_list(data: list[TypeEncodable]) -> bytes:
    """Encode a list object into bencode.

    :param value: The value to encode
    :return: The value encoded in bencode
    """
    result = [LIST]
    for element in data:
        result.append(encode(element))
    result.append(END)
    return b"".join(result)


def _encode_str(value: str) -> bytes:
    """Encode a str object into bencode.

    :param value: The value to encode
    :return: The value encoded in bencode
    """
    return _encode_bytes(value.encode(ENCODING))


def encode(data: TypeEncodable) -> bytes:
    """Encode a typeencodeable object into bencode.

    :param data: The data to encode
    :return: The data encoded in bencode
    :raises BencodeEncodeError: If can't encode the data
    """
    if isinstance(data, bool):
        return _encode_bool(data)
    if isinstance(data, bytes):
        return _encode_bytes(data)
    if isinstance(data, dict):
        return _encode_dict(data)
    if isinstance(data, int):
        return _encode_int(data)
    if isinstance(data, list):
        return _encode_list(data)
    if isinstance(data, str):
        return _encode_str(data)

    raise BencodeEncodeError(f"Unsupported type: {type(data)}")


def _decode_int(data: bytes, i: int) -> tuple[int, int]:
    """Decode an int from a bencode object.

    :param data: A bencode object
    :param i: The index to start parsing an int from
    :return: The int and the end index inside the bencode object
    """
    i += 1
    end_idx = data.index(END, i)
    num = int(data[i:end_idx])
    return num, end_idx + 1


def _decode_str(data: bytes, i: int) -> tuple[Union[str, bytes], int]:
    """Decode a str from a bencode object.

    :param data: A bencode object
    :param i: The index to start parsing a str from
    :return: The str and the end index inside the bencode object
    """
    colon_idx = data.index(COLON, i)
    length = int(data[i:colon_idx])
    start = colon_idx + 1
    byte_string = data[start : start + length]
    try:
        result: Union[str, bytes] = byte_string.decode(ENCODING)
    except UnicodeDecodeError:
        # Considered to be a bytestring (e.g. `pieces` hashes concatenation).
        result = byte_string
    return result, start + length


def _decode_dict(
    data: bytes, i: int
) -> tuple[dict[Union[str, bytes], TypeEncodable], int]:
    """Decode a dict from a bencode object.

    :param data: A bencode object
    :param i: The index to start parsing a dict from
    :return: The dict and the end index inside the bencode object
    """
    i += 1
    result = {}
    while data[i : i + 1] != END:
        key, i = _decode_str(data, i)
        result[key], i = _decode(data, i)
    return result, i + 1


def _decode_list(data: bytes, i: int) -> tuple[list[TypeEncodable], int]:
    """Decode a list from a bencode object.

    :param data: A bencode object
    :param i: The index to start parsing a list from
    :return: The list and the end index inside the bencode object
    """
    i += 1
    items = []
    while data[i : i + 1] != END:
        item, i = _decode(data, i)
        items.append(item)
    return items, i + 1


def _decode(encoded: bytes, i: int) -> tuple[TypeEncodable, int]:
    """Decode a bencode-encoded object starting from an index.
    Helper function for the parent decode function

    :param encoded: A bencode-encoded object
    :param i: The index into the bencode object to start decoding
    :return: The object as a TypeEncodable
    :raises BencodeDecodeError: if can't decode
    """
    char = encoded[i : i + 1]

    if char == INTEGER:
        return _decode_int(encoded, i)
    if char.isdigit():
        return _decode_str(encoded, i)
    if char == DICT:
        return _decode_dict(encoded, i)
    if char == LIST:
        return _decode_list(encoded, i)

    raise BencodeDecodeError


def decode(data: Union[bytes, str]) -> TypeEncodable:
    """Decode a bencode-encoded object into TypeEncodable.

    :param data: A bencode-encoded object
    :return: The object as a TypeEncodable
    :raises BencodeDecodeError: if can't decode
    """
    if isinstance(data, str):
        data = data.encode(ENCODING, "strict")

    result, length = _decode(data, 0)
    if len(data) != length:
        raise BencodeDecodeError
    return result


@pytest.mark.parametrize(
    "test_input,expected",
    [(0, b"i0e"), (1, b"i1e"), (10, b"i10e"), (42, b"i42e"), (-42, b"i-42e")],
)
def test_encode_integer(test_input: int, expected: bytes) -> None:
    """Test encode_integer."""
    assert _encode_int(test_input) == expected


@pytest.mark.parametrize("test_input,expected", [(True, b"i1e"), (False, b"i0e")])
def test_encode_bool(test_input: bool, expected: bytes) -> None:
    """Test encode_bool."""
    assert _encode_bool(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [(b"spam", b"4:spam"), (b"parrot sketch", b"13:parrot sketch")],
)
def test_encode_bytes(test_input: bytes, expected: bytes) -> None:
    """Test encode_bytes."""
    assert _encode_bytes(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected", [([b"parrot sketch", 42], b"l13:parrot sketchi42ee")]
)
def test_encode_list(test_input: list[TypeEncodable], expected: bytes) -> None:
    """Test encode_list."""
    assert _encode_list(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({b"foo": 42, b"bar": b"spam"}, b"d3:bar4:spam3:fooi42ee"),
        (
            {"foo": 42, "bar": {"sketch": "parrot", "foobar": 23}},
            b"d3:bard6:foobari23e6:sketch6:parrote3:fooi42ee",
        ),
    ],
)
def test_encode_dict(test_input: dict[str, TypeEncodable], expected: bytes) -> None:
    """Test encode_dict."""
    assert _encode_dict(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected", [("parrot sketch", b"13:parrot sketch")]
)
def test_encode_str(test_input: str, expected: bytes) -> None:
    """Test encode_str."""
    assert _encode_str(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected", [(b"13:parrot sketch", "parrot sketch")]
)
def test_decode_str(test_input: str, expected: bytes) -> None:
    """Test decode_str."""
    assert decode(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (b"d3:bar4:spam3:fooi42ee", {"bar": "spam", "foo": 42}),
        (
            b"d3:bard6:foobari23e6:sketch6:parrote3:fooi42ee",
            {"bar": {"foobar": 23, "sketch": "parrot"}, "foo": 42},
        ),
    ],
)
def test_decode_dict(test_input: str, expected: bytes) -> None:
    """Test decode_dict."""
    assert decode(test_input) == expected
