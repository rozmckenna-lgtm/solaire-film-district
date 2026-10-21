#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path
from gamma_sync_guard import validate

class GammaSyncGuardTests(unittest.TestCase):
    def setUp(self):
        self.manifest={"syncEnabled":False,"articles":[
            {"localPath":"does-a-story-have-to-be-fast.html","gammaId":"annfffa1kk0wj44","verifiedCanonical":True},
            {"localPath":"john-malkovich.html","gammaId":"jb54fepsfow64in","verifiedCanonical":False}
        ]}
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/"in").mkdir()
    def run_guard(self):
        return validate(self.manifest,self.root/"in",self.root/"out")
    def test_missing_authenticated_export_does_not_write(self):
        result=self.run_guard()
        self.assertEqual([x["status"] for x in result],["MISSING_AUTHENTICATED_EXPORT","SKIPPED_UNVERIFIED"])
        self.assertFalse((self.root/"out").exists())
    def test_unrelated_french_source_rejected(self):
        (self.root/"in"/"annfffa1kk0wj44.txt").write_text("Title: COMMENT FINANCER MON FILM ?\n<div><section><h1>Wrong</h1></section></div>")
        result=self.run_guard()
        self.assertEqual(result[0]["status"],"REJECTED")
        self.assertFalse((self.root/"out"/"does-a-story-have-to-be-fast.html").exists())
    def test_sync_enabled_cannot_run_guard(self):
        self.manifest["syncEnabled"]=True
        with self.assertRaises(ValueError):self.run_guard()
    def test_path_traversal_rejected(self):
        self.manifest["articles"][0]["localPath"]="../index.html"
        self.assertEqual(self.run_guard()[0]["status"],"SKIPPED_UNVERIFIED")
    def test_valid_english_source_creates_only_dry_run_fragment(self):
        title="Does a Story Have to Be Fast to Be Compelling?"
        paragraphs="".join("<p>English source paragraph about screenplay structure and narrative pacing.</p>" for _ in range(12))
        source=f"Title: {title}\n<div><section><h1>{title}</h1>{paragraphs}</section></div>"
        (self.root/"in"/"annfffa1kk0wj44.txt").write_text(source,encoding="utf-8")
        result=self.run_guard()
        self.assertEqual(result[0]["status"],"DRY_RUN_VALIDATED")
        target=self.root/"out"/"does-a-story-have-to-be-fast.html"
        self.assertTrue(target.is_file())
        self.assertIn('lang="en"',target.read_text())
        self.assertFalse((self.root/"does-a-story-have-to-be-fast.html").exists())
        self.assertEqual(result[1]["status"],"SKIPPED_UNVERIFIED")
    def test_dry_run_refuses_overwrite(self):
        title="Does a Story Have to Be Fast to Be Compelling?"
        paragraphs="".join("<p>English source paragraph about screenplay structure and narrative pacing.</p>" for _ in range(12))
        (self.root/"in"/"annfffa1kk0wj44.txt").write_text(f"Title: {title}\n<div><section><h1>{title}</h1>{paragraphs}</section></div>")
        first=self.run_guard()
        self.assertEqual(first[0]["status"],"DRY_RUN_VALIDATED")
        second=self.run_guard()
        self.assertEqual(second[0]["status"],"REJECTED")
        self.assertIn("overwrite",second[0]["reason"])
if __name__=="__main__": unittest.main()
