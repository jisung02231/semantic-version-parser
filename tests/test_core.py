import unittest
from semantic_version_parser import Version, parse, ParseError

class TestParse(unittest.TestCase):
    def test_simple(self):
        v = parse("1.2.3")
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 2)
        self.assertEqual(v.patch, 3)
        self.assertEqual(v.prerelease, ())
        self.assertEqual(v.build, ())
    def test_prerelease(self):
        v = parse("1.0.0-alpha")
        self.assertEqual(v.prerelease, ("alpha",))
        self.assertTrue(v.has_prerelease)
    def test_build(self):
        v = parse("1.0.0+build.42")
        self.assertEqual(v.build, ("build", "42"))
        self.assertTrue(v.has_build)
    def test_full(self):
        v = parse("1.2.3-rc.1+exp.sha.5114f85")
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 2)
        self.assertEqual(v.patch, 3)
        self.assertEqual(v.prerelease, ("rc", "1"))
        self.assertEqual(v.build, ("exp", "sha", "5114f85"))
    def test_strip_whitespace(self):
        v = parse("  1.0.0  \n")
        self.assertEqual(v.major, 1)
    def test_zero_versions(self):
        v = parse("0.0.0")
        self.assertEqual(v.core, (0, 0, 0))
    def test_numeric_prerelease(self):
        v = parse("1.0.0-1.2.3")
        self.assertEqual(v.prerelease, ("1", "2", "3"))

class TestErrors(unittest.TestCase):
    def test_empty(self):
        with self.assertRaises(ParseError):
            parse("")
    def test_leading_zero_major(self):
        with self.assertRaises(ParseError):
            parse("01.0.0")
    def test_leading_zero_minor(self):
        with self.assertRaises(ParseError):
            parse("1.01.0")
    def test_leading_zero_patch(self):
        with self.assertRaises(ParseError):
            parse("1.0.01")
    def test_leading_zero_pre_numeric(self):
        with self.assertRaises(ParseError):
            parse("1.0.0-01")
    def test_missing_patch(self):
        with self.assertRaises(ParseError):
            parse("1.0")
    def test_non_string(self):
        with self.assertRaises(ParseError):
            parse(123)
    def test_build_empty_identifier(self):
        with self.assertRaises(ParseError):
            parse("1.0.0+foo..bar")
    def test_pre_empty_identifier(self):
        with self.assertRaises(ParseError):
            parse("1.0.0-alpha..beta")
    def test_invalid_char(self):
        with self.assertRaises(ParseError):
            parse("1.0.0-alpha_beta")
    def test_v_prefix(self):
        with self.assertRaises(ParseError):
            parse("v1.0.0")

class TestStringRoundtrip(unittest.TestCase):
    def test_roundtrip_simple(self):
        self.assertEqual(str(parse("1.2.3")), "1.2.3")
    def test_roundtrip_pre(self):
        self.assertEqual(str(parse("1.0.0-alpha.1")), "1.0.0-alpha.1")
    def test_roundtrip_build(self):
        self.assertEqual(str(parse("1.0.0+20130313144700")), "1.0.0+20130313144700")
    def test_roundtrip_full(self):
        self.assertEqual(str(parse("1.2.3-rc.1+exp.sha.5114f85")), "1.2.3-rc.1+exp.sha.5114f85")

class TestComparison(unittest.TestCase):
    def test_major_diff(self):
        self.assertTrue(parse("1.0.0") < parse("2.0.0"))
    def test_minor_diff(self):
        self.assertTrue(parse("1.0.0") < parse("1.1.0"))
    def test_patch_diff(self):
        self.assertTrue(parse("1.0.0") < parse("1.0.1"))
    def test_pre_lower_than_release(self):
        self.assertTrue(parse("1.0.0-alpha") < parse("1.0.0"))
    def test_pre_numeric_lower_than_alpha(self):
        self.assertTrue(parse("1.0.0-1") < parse("1.0.0-alpha"))
    def test_pre_numeric_compare(self):
        self.assertTrue(parse("1.0.0-2") < parse("1.0.0-10"))
    def test_pre_alpha_compare(self):
        self.assertTrue(parse("1.0.0-alpha") < parse("1.0.0-beta"))
    def test_pre_fewer_fields_lower(self):
        self.assertTrue(parse("1.0.0-alpha") < parse("1.0.0-alpha.1"))
    def test_equal(self):
        self.assertEqual(parse("1.0.0"), parse("1.0.0"))
    def test_equal_ignores_build(self):
        self.assertEqual(parse("1.0.0+a"), parse("1.0.0+b"))
    def test_ge(self):
        self.assertTrue(parse("1.0.0") >= parse("1.0.0"))
        self.assertTrue(parse("1.0.0") >= parse("0.9.0"))
    def test_le(self):
        self.assertTrue(parse("1.0.0") <= parse("1.0.0"))
        self.assertTrue(parse("1.0.0") <= parse("1.0.1"))
    def test_gt(self):
        self.assertTrue(parse("2.0.0") > parse("1.0.0"))

class TestVersionDirect(unittest.TestCase):
    def test_construct(self):
        v = Version(1, 2, 3, ("alpha",), ("b",))
        self.assertEqual(v.major, 1)
        self.assertEqual(v.prerelease, ("alpha",))
        self.assertEqual(v.build, ("b",))
    def test_repr(self):
        v = Version(1, 0, 0)
        self.assertIn("Version(", repr(v))
        self.assertIn("1", repr(v))
    def test_hash(self):
        a = parse("1.0.0")
        b = parse("1.0.0")
        self.assertEqual(hash(a), hash(b))
    def test_eq_non_version(self):
        v = parse("1.0.0")
        self.assertFalse(v == "1.0.0")
        self.assertNotEqual(v, "1.0.0")

class TestBuildIdentifiers(unittest.TestCase):
    def test_build_allows_leading_zero(self):
        v = parse("1.0.0+001")
        self.assertEqual(v.build, ("001",))
    def test_build_alphanumeric(self):
        v = parse("1.0.0+sha.abc123")
        self.assertEqual(v.build, ("sha", "abc123"))

class TestPrereleaseIdentifiers(unittest.TestCase):
    def test_hyphen_in_ident(self):
        v = parse("1.0.0-alpha-1")
        self.assertEqual(v.prerelease, ("alpha-1",))
    def test_mixed(self):
        v = parse("1.0.0-0.alpha.1")
        self.assertEqual(v.prerelease, ("0", "alpha", "1"))

if __name__ == "__main__":
    unittest.main()
