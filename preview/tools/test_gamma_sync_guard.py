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
if __name__=="__main__": unittest.main()
