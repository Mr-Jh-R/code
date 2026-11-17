"""Behavior tests with a local Git fixture; no remote network or user store writes."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import standards_store as store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.cache = self.root / "cache"
        self.run_git("init")
        self.run_git("config", "user.name", "Fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.run_git("config", "core.autocrlf", "false")
        self.run_git("remote", "add", "origin", store.SOURCE)
        files = {
            "VERSION": "2.4.0\n", "LICENSE": "fixture license\n",
            "conventions/backend-conventions.md": "Backend routing\n",
            "conventions/backend/core.md": "Common rules\n",
            "conventions/frontend-conventions.md": "Frontend routing\n",
            "conventions/frontend-conventions-react.md": "React rules\n",
            "conventions/backend/databases/mysql.md": "MySQL rules\n",
            "conventions/backend/languages/java.md": "Java rules\n",
        }
        for name, text in files.items():
            file = self.repo / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(text, encoding="utf-8")
        self.run_git("add", ".")
        self.run_git("commit", "-m", "fixture")
        self.run_git("tag", "-a", "v2.4.0", "-m", "fixture release")
        self.sha = self.run_git("rev-parse", "HEAD")

    def run_git(self, *args):
        result = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, check=True)
        return result.stdout.decode().strip()

    def test_export_uses_commit_and_preserves_existing_version(self):
        (self.repo / "conventions/backend/core.md").write_text("dirty", encoding="utf-8")
        one = store.install(self.cache, self.repo, "v2.4.0")
        self.assertEqual((Path(one["root"]) / "conventions/backend/core.md").read_text(), "Common rules\n")
        self.assertEqual(one, store.install(self.cache, self.repo, "v2.4.0"))
        self.assertFalse((self.cache / "selection.json").exists())

    def test_tag_and_development_commit_are_distinct(self):
        store.install(self.cache, self.repo, "v2.4.0")
        snapshot = store.install(self.cache, self.repo, self.sha)
        self.assertEqual(snapshot["id"], "snapshot-" + self.sha)
        self.assertEqual(snapshot["kind"], "snapshot")
        self.assertEqual(len(store.inventory(self.cache)["versions"]), 2)

    def test_selection_required_even_with_one_version_and_no_network(self):
        store.install(self.cache, self.repo, "v2.4.0")
        with patch.object(store.subprocess, "run", side_effect=AssertionError("Offline command ran subprocess")):
            self.assertEqual(store.resolve(self.cache)["status"], "selection_required")
            self.assertFalse(store.inventory(self.cache)["upstream_checked"])
            self.assertEqual(store.resolve(self.cache, explicit="v2.4.0")["selection"], "explicit")

    def test_precedence_and_missing_pin_do_not_fall_back(self):
        store.install(self.cache, self.repo, "v2.4.0")
        snapshot = store.install(self.cache, self.repo, self.sha)["id"]
        (self.cache / "selection.json").write_text(json.dumps({"default": "v2.4.0"}))
        self.assertEqual(store.resolve(self.cache, session=snapshot, project="v2.4.0")["id"], snapshot)
        self.assertEqual(store.resolve(self.cache, explicit="v2.4.0", session=snapshot)["id"], "v2.4.0")
        self.assertEqual(store.resolve(self.cache, project=snapshot)["id"], snapshot)
        with self.assertRaises(OSError):
            store.resolve(self.cache, project="v2.9.0")

    def test_tampered_missing_and_extra_files_are_invalid(self):
        item = store.install(self.cache, self.repo, "v2.4.0")
        root = Path(item["root"])
        path = root / "conventions/backend/core.md"
        original = path.read_bytes()
        for action in (lambda: path.write_text("changed"), lambda: path.unlink()):
            action()
            with self.assertRaises((ValueError, OSError)):
                store.verify(self.cache, "v2.4.0")
            self.assertEqual(len(store.inventory(self.cache)["invalid"]), 1)
            path.write_bytes(original)
        (root / "unexpected.md").write_text("untracked rules")
        with self.assertRaises(ValueError):
            store.verify(self.cache, "v2.4.0")

    def test_moved_tag_cannot_overwrite_cache(self):
        item = store.install(self.cache, self.repo, "v2.4.0")
        (self.repo / "conventions/backend/core.md").write_text("new rules")
        self.run_git("add", ".")
        self.run_git("commit", "-m", "changed fixture")
        self.run_git("tag", "-f", "v2.4.0")
        with self.assertRaises(ValueError):
            store.install(self.cache, self.repo, "v2.4.0")
        self.assertEqual(store.verify(self.cache, "v2.4.0")["commit"], item["commit"])

    def test_source_and_version_mismatch_and_mutable_ref_rejected(self):
        with self.assertRaises(ValueError):
            store.install(self.cache, self.repo, "HEAD")
        self.run_git("tag", "v2.5.0")
        with self.assertRaises(ValueError):
            store.install(self.cache, self.repo, "v2.5.0")
        self.run_git("remote", "set-url", "origin", "https://example.invalid/code.git")
        with self.assertRaises(ValueError):
            store.install(self.cache, self.repo, "v2.4.0")

    def test_path_escape_rejected(self):
        for version in ("../other", "v2.4.0/../../other", "snapshot-1234"):
            with self.assertRaises(ValueError):
                store.verify(self.cache, version)
        for name in ("../outside", "/absolute", "C:/outside", "a\\b"):
            with self.assertRaises(ValueError):
                store.safe_path(self.root, name)

    def test_react_plan_reaches_real_rules(self):
        item = store.install(self.cache, self.repo, "v2.4.0")
        with patch.object(store.subprocess, "run", side_effect=AssertionError("Network not allowed")):
            result = store.reading_plan(item, frontend="react")
        paths = [Path(f["path"]).name for f in result["files"]]
        self.assertEqual(paths, ["frontend-conventions.md", "frontend-conventions-react.md"])
        self.assertEqual(result["missing_appendices"], [])

    def test_python_mysql_uses_common_rules_not_java(self):
        item = store.install(self.cache, self.repo, "v2.4.0")
        result = store.reading_plan(item, backend=True, language="python", databases=["mysql"])
        names = [Path(f["path"]).name for f in result["files"]]
        self.assertIn("core.md", names)
        self.assertIn("mysql.md", names)
        self.assertNotIn("java.md", names)
        self.assertEqual(result["missing_appendices"], ["backend/languages/python.md"])

    def test_updates_sorts_stable_tags_and_peels_annotated_tag(self):
        output = ("a" * 40 + "\trefs/tags/v2.9.0\n" + "b" * 40 + "\trefs/tags/v2.10.0\n"
                  + "c" * 40 + "\trefs/tags/v2.10.0^{}\n" + "d" * 40 + "\trefs/tags/v3.0.0-rc1\n")
        with patch.object(store.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, output.encode(), b"")):
            versions = store.updates()["releases"]
        self.assertEqual([v["id"] for v in versions], ["v2.10.0", "v2.9.0"])
        self.assertEqual(versions[0]["commit"], "c" * 40)

    def test_cli_works_outside_repository_and_saves_only_explicit_default(self):
        store.install(self.cache, self.repo, "v2.4.0")
        command = [store.sys.executable, "-B", str(Path(store.__file__).resolve()), "--store", str(self.cache)]
        pending = subprocess.run(command + ["resolve"], cwd=self.root, capture_output=True)
        self.assertEqual(pending.returncode, 2)
        self.assertEqual(json.loads(pending.stdout)["status"], "selection_required")
        setting = subprocess.run(command + ["default", "--version", "v2.4.0"], cwd=self.root, capture_output=True)
        self.assertEqual(setting.returncode, 0, setting.stderr)
        resolved = subprocess.run(command + ["resolve"], cwd=self.root, capture_output=True)
        self.assertEqual(json.loads(resolved.stdout)["selection"], "default")
        self.assertEqual(json.loads(resolved.stdout)["commit"], self.sha)

    def test_git_link_blob_is_rejected_without_writing_snapshot(self):
        result = subprocess.run(["git", "-C", str(self.repo), "hash-object", "-w", "--stdin"],
                                input=b"../../outside", capture_output=True, check=True)
        self.run_git("update-index", "--add", "--cacheinfo", "120000", result.stdout.decode().strip(), "conventions/linked.md")
        self.run_git("commit", "-m", "link fixture")
        sha = self.run_git("rev-parse", "HEAD")
        with self.assertRaises(ValueError):
            store.install(self.cache, self.repo, sha)
        self.assertFalse(self.cache.exists())


if __name__ == "__main__":
    unittest.main()
