#!/usr/bin/env python3
"""No-network safety tests for Gamma article conversion."""
import unittest
from convert_gamma_article import convert

def sample(title):
    return "Title: " + title + "\n<div><section><h1>" + title + "</h1><p>" + ("A meaningful English paragraph. " * 35) + "</p></section></div>"

class ConverterTests(unittest.TestCase):
    def test_expected_english_source(self):
        html = convert(sample("An English Story"), "An English Story")
        self.assertIn('lang="en"', html)
        self.assertIn("A meaningful English paragraph", html)
    def test_unrelated_source_is_rejected(self):
        with self.assertRaises(ValueError):
            convert(sample("COMMENT FINANCER MON FILM ?"), "An English Story")
    def test_wrong_english_source_is_rejected(self):
        with self.assertRaises(ValueError):
            convert(sample("Another English Story"), "An English Story")
    def test_missing_title_is_rejected(self):
        with self.assertRaises(ValueError):
            convert("<div><section><h1>English</h1><p>" + "text " * 300 + "</p></section></div>", "An English Story")
    def test_script_markup_does_not_execute(self):
        html = convert(sample("An English Story").replace("</p>", "<script>alert(1)</script></p>"), "An English Story")
        self.assertNotIn("<script", html)

if __name__ == "__main__":
    unittest.main()
