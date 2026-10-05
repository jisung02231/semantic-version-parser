# Semantic Version Parser

Parses SemVer 2.0 version strings into major, minor, patch, prerelease, and build components. Zero third-party dependencies; standard library only.

## Usage

```python
from semantic_version_parser import parse, Version, ParseError

v = parse("1.2.3-rc.1+exp.sha.5114f85")
print(v.major, v.minor, v.patch)  # 1 2 3
print(v.prerelease)               # ('rc', '1')
print(v.build)                    # ('exp', 'sha', '5114f85')
print(str(v))                     # 1.2.3-rc.1+exp.sha.5114f85

# Comparison follows SemVer precedence rules.
parse("1.0.0-alpha") < parse("1.0.0")   # True
parse("1.0.0-1") < parse("1.0.0-2")     # True (numeric prerelease compare)

# Build metadata is ignored for equality and ordering.
parse("1.0.0+a") == parse("1.0.0+b")     # True

try:
    parse("01.0.0")
except ParseError as e:
    print(e)  # invalid semantic version: '01.0.0'
```

## Exports

- `parse(text)` — returns a `Version` or raises `ParseError`.
- `Version` — the parsed result. Attributes: `major`, `minor`, `patch` (ints), `prerelease` and `build` (tuples of strings). Supports `==`, `<`, `<=`, `>`, `>=`, `hash`, `str`, `repr`.
- `ParseError` — subclass of `ValueError`, raised on any invalid input.

## Why

Needed a strict SemVer 2.0 parser with no external dependencies for an environment where `pip install` is unavailable. The trade-off: this library only parses and compares. It does not do range matching (`^1.2.3`, `~1.0`, `>=1.0 <2.0`). If you need ranges, this is the wrong library.

## Edge cases

- Leading zeros are rejected in `major`, `minor`, `patch`, and numeric prerelease identifiers, per spec. Build identifiers may have leading zeros (build metadata is not compared).
- A `v` prefix (`v1.0.0`) is rejected. The spec says the version is `MAJOR.MINOR.PATCH`; a `v` is not part of it.
- Input is stripped of surrounding whitespace before parsing.
- Build metadata is ignored for equality and ordering, so `1.0.0+a == 1.0.0+b` and both compare equal to `1.0.0`.
- Prerelease comparison: numeric identifiers compare as integers (so `2 < 10`); alphanumeric compare lexically; numeric always ranks below alphanumeric; fewer fields ranks below more fields when all preceding fields are equal.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

