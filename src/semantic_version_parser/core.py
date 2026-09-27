import re

__version__ = "1.0.0"

class ParseError(ValueError):
    pass

_NUMERIC = re.compile(r"^[0-9]+$")
_IDENT = re.compile(r"^(0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)$")
_BUILD_IDENT = re.compile(r"^[0-9A-Za-z-]+$")
_FULL = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)

class Version:
    __slots__ = ("major", "minor", "patch", "prerelease", "build")
    def __init__(self, major, minor, patch, prerelease=None, build=None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = tuple(prerelease) if prerelease else ()
        self.build = tuple(build) if build else ()
    @property
    def has_prerelease(self):
        return bool(self.prerelease)
    @property
    def has_build(self):
        return bool(self.build)
    @property
    def core(self):
        return (self.major, self.minor, self.patch)
    def __str__(self):
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            s += "-" + ".".join(self.prerelease)
        if self.build:
            s += "+" + ".".join(self.build)
        return s
    def __repr__(self):
        return f"Version(major={self.major!r}, minor={self.minor!r}, patch={self.patch!r}, prerelease={list(self.prerelease)!r}, build={list(self.build)!r})"
    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch, self.prerelease) == (other.major, other.minor, other.patch, other.prerelease)
    def __hash__(self):
        return hash((self.major, self.minor, self.patch, self.prerelease))
    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        if self.core != other.core:
            return self.core < other.core
        if not self.prerelease and not other.prerelease:
            return False
        if self.prerelease and not other.prerelease:
            return True
        if not self.prerelease and other.prerelease:
            return False
        return _cmp_pre(self.prerelease, other.prerelease) < 0
    def __le__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self == other or self < other
    def __gt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return other < self
    def __ge__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self == other or self > other

def _cmp_pre(a, b):
    for x, y in zip(a, b):
        xn = _NUMERIC.match(x) is not None
        yn = _NUMERIC.match(y) is not None
        if xn and yn:
            xi, yi = int(x), int(y)
            if xi != yi:
                return -1 if xi < yi else 1
        elif xn and not yn:
            return -1
        elif not xn and yn:
            return 1
        else:
            if x != y:
                return -1 if x < y else 1
    return len(a) - len(b)

def _validate_identifiers(s, kind):
    parts = s.split(".")
    for p in parts:
        if p == "":
            raise ParseError(f"empty {kind} identifier")
        if _NUMERIC.match(p) and not (p == "0" or not p.startswith("0")):
            raise ParseError(f"numeric {kind} identifier has leading zero: {p!r}")
        if not _IDENT.match(p):
            raise ParseError(f"invalid {kind} identifier: {p!r}")
    return parts

def parse(text):
    if not isinstance(text, str):
        raise ParseError("input must be a string")
    s = text.strip()
    if not s:
        raise ParseError("empty input")
    m = _FULL.match(s)
    if m is None:
        raise ParseError(f"invalid semantic version: {text!r}")
    major, minor, patch, pre, build = m.groups()
    pre_parts = _validate_identifiers(pre, "prerelease") if pre is not None else ()
    build_parts = build.split(".") if build is not None else ()
    for bp in build_parts:
        if bp == "":
            raise ParseError("empty build identifier")
        if not _BUILD_IDENT.match(bp):
            raise ParseError(f"invalid build identifier: {bp!r}")
    return Version(int(major), int(minor), int(patch), pre_parts, build_parts)
