import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate.py"
SPEC = importlib.util.spec_from_file_location("factory_validate", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write(".claude-plugin/plugin.json", '{"name": "devin-factory"}')
        self.write("README.md", "\n".join(sorted(validator.SKILLS)))
        for name in validator.SKILLS:
            self.write(f"skills/{name}/SKILL.md",
                       f"---\nname: {name}\ndescription: A concrete skill.\n---\nSteps.\n")
        for name in validator.SCHEMAS:
            self.write(f"schemas/{name}.json", json.dumps({"$schema": validator.DRAFT_07}))
        for name in validator.AUTOMATIONS:
            self.write(f"automations/{name}.json", json.dumps({
                "action": {"session": {"prompt": "@skills:factory-foreman"}}
            }))

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def assert_error(self, expected):
        errors = validator.validate(self.root)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_valid_repository(self):
        self.assertEqual(validator.validate(self.root), [])

    def test_actual_repository(self):
        self.assertEqual(validator.validate(MODULE_PATH.parents[1]), [])

    def test_empty_repository(self):
        with tempfile.TemporaryDirectory() as empty:
            errors = validator.validate(Path(empty))
        self.assertTrue(any("plugin.json: cannot read" in error for error in errors))
        self.assertTrue(any("missing required skill" in error for error in errors))
        self.assertTrue(any("missing required schema" in error for error in errors))
        self.assertTrue(any("missing required automation" in error for error in errors))

    def test_invalid_plugin_json(self):
        self.write(".claude-plugin/plugin.json", "{")
        self.assert_error("invalid JSON")

    def test_nonobject_plugin(self):
        self.write(".claude-plugin/plugin.json", "[]")
        self.assert_error("expected a JSON object")

    def test_missing_plugin(self):
        (self.root / ".claude-plugin/plugin.json").unlink()
        self.assert_error("plugin.json: cannot read")

    def test_missing_frontmatter(self):
        self.write("skills/factory-triage/SKILL.md", "No frontmatter.")
        self.assert_error("frontmatter name must match")

    def test_unclosed_frontmatter(self):
        self.write("skills/factory-triage/SKILL.md", "---\nname: factory-triage")
        self.assert_error("frontmatter name must match")

    def test_wrong_skill_name(self):
        self.write("skills/factory-triage/SKILL.md",
                   "---\nname: wrong\ndescription: Triage.\n---\n")
        self.assert_error("frontmatter name must match directory factory-triage")

    def test_empty_description(self):
        self.write("skills/factory-triage/SKILL.md",
                   "---\nname: factory-triage\ndescription: ''\n---\n")
        self.assert_error("description must be nonempty")

    def test_missing_description(self):
        self.write("skills/factory-triage/SKILL.md", "---\nname: factory-triage\n---\n")
        self.assert_error("description must be nonempty")

    def test_quoted_frontmatter(self):
        self.write("skills/factory-triage/SKILL.md",
                   "---\nname: 'factory-triage'\ndescription: \"Triage: inspect scope.\"\n---\n")
        self.assertEqual(validator.validate(self.root), [])

    def test_missing_skill_file(self):
        (self.root / "skills/factory-triage/SKILL.md").unlink()
        self.assert_error("SKILL.md: cannot read")

    def test_invalid_utf8(self):
        (self.root / "skills/factory-triage/SKILL.md").write_bytes(b"\xff")
        self.assert_error("cannot read")

    def test_schema_invalid_json(self):
        self.write("schemas/state.json", "{bad")
        self.assert_error("invalid JSON")

    def test_schema_missing_declaration(self):
        self.write("schemas/state.json", "{}")
        self.assert_error("$schema must be")

    def test_wrong_schema_draft(self):
        self.write("schemas/state.json", '{"$schema": "draft-2020-12"}')
        self.assert_error("$schema must be")

    def test_missing_schema(self):
        (self.root / "schemas/state.json").unlink()
        self.assert_error("missing required schema state.json")

    def test_automation_invalid_json(self):
        self.write("automations/A1-intake.json", "{")
        self.assert_error("invalid JSON")

    def test_unknown_skill_reference(self):
        self.write("automations/A1-intake.json",
                   '{"nested": [{"prompt": "@skills:does-not-exist"}]}')
        self.assert_error("unknown skill does-not-exist")

    def test_all_references_are_checked(self):
        self.write("automations/A1-intake.json", json.dumps({
            "prompt": "@skills:factory-foreman and @skills:missing"
        }))
        self.assert_error("unknown skill missing")

    def test_missing_automation_reference(self):
        self.write("automations/A1-intake.json", "{}")
        self.assert_error("no @skills: reference")

    def test_missing_automation(self):
        (self.root / "automations/A1-intake.json").unlink()
        self.assert_error("missing required automation A1-intake.json")

    def test_readme_must_mention_every_skill(self):
        self.write("README.md", "\n".join(sorted(validator.SKILLS - {"factory-triage"})))
        self.assert_error("README.md: missing skill factory-triage")

    def test_readme_prefix_does_not_count(self):
        self.write("README.md", "\n".join(sorted(validator.SKILLS)).replace(
            "factory-triage", "factory-triage-extra"))
        self.assert_error("README.md: missing skill factory-triage")

    def test_cli_success(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = validator.main([str(self.root)])
        self.assertEqual(result, 0)
        self.assertIn("Validation passed:", output.getvalue())

    def test_cli_failure(self):
        self.write(".claude-plugin/plugin.json", "null")
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            result = validator.main([str(self.root)])
        self.assertEqual(result, 1)
        self.assertIn("Validation failed:", output.getvalue())


class SkillPolicyTests(unittest.TestCase):
    def skill_text(self, name):
        path = MODULE_PATH.parents[1] / "skills" / name / "SKILL.md"
        return " ".join(path.read_text(encoding="utf-8").split())

    def test_watchdog_excludes_intake_and_missing_state(self):
        text = self.skill_text("factory-watchdog")
        self.assertIn("Always skip Factory › intake, even with state; A1 owns intake.", text)
        self.assertIn("Skip issues with no state comment: missing state is not stale.", text)
        self.assertIn("Never start or resume either case.", text)

    def test_watchdog_requires_stale_single_state_and_finished_owner(self):
        text = self.skill_text("factory-watchdog")
        self.assertIn("Act only when exactly one valid state comment exists", text)
        self.assertIn("updated_at is strictly more than six hours old", text)
        self.assertIn("AND its owner is verified finished/unreachable", text)
        self.assertIn("skip live owners without nudging them", text)
        self.assertIn("immediately before recovery; skip if any gate no longer holds", text)

    def test_foreman_and_state_define_losing_claim_cleanup(self):
        for name in ("factory-foreman", "factory-linear-state"):
            with self.subTest(skill=name):
                text = self.skill_text(name)
                self.assertIn("earliest-created state comment wins", text)
                self.assertIn("comment id ascending", text)
                self.assertIn("re-read all comment pages", text)
                self.assertIn("delete only your own state comment", text)
                self.assertIn("cancel only children you started", text)
                self.assertIn("post nothing else and end your own session", text)
                self.assertIn("resume", text)

    def test_one_shot_helpers_end_but_dispatcher_waits(self):
        watchdog = self.skill_text("factory-watchdog")
        relay = self.skill_text("factory-relay")
        self.assertIn("end your own one-shot session", watchdog)
        self.assertIn("One-shot: after reporting, end your own session", relay)
        self.assertIn("Dispatcher: after every result return to waiting", relay)
        for text in (watchdog, relay):
            self.assertIn("devin_session_interact or host equivalent", text)

    def test_android_build_delegates_and_reuses_same_child(self):
        text = self.skill_text("factory-build")
        self.assertIn("vmm android/ or scarlet-team-c-android", text)
        self.assertIn("On macOS or without accessible /dev/kvm, start ONE Linux child for the same repo", text)
        self.assertIn("exact PR head SHA", text)
        self.assertIn("Reuse the same Android child for revisions", text)
        self.assertIn("Cancel the Android child on stop", text)
        self.assertIn("map checks/evidence/blockers into schemas/build.json", text)

    def test_android_empty_and_error_evidence_cannot_pass(self):
        text = self.skill_text("factory-build")
        self.assertIn("Never mark Android checks passed without current-head Android child evidence", text)
        self.assertIn("Empty checks/evidence, inaccessible KVM, failed checks or a lost child", text)
        self.assertIn("never ready", text)
        gates = self.skill_text("factory-repo-gates")
        self.assertIn("Missing, empty or stale Android evidence is not a pass", gates)
        review = self.skill_text("factory-review")
        self.assertIn("Missing, empty, inaccessible or stale Android evidence is a human item, never accept", review)

    def test_android_runtime_contract_and_manual_claude_fallback(self):
        runtime = MODULE_PATH.parents[1] / "runtime"
        text = (runtime / "devin.md").read_text(encoding="utf-8")
        self.assertIn('**platform: "linux"**', text)
        self.assertIn("notify_on_response=true", text)
        self.assertIn("not a new state.children key", text)
        schema = json.loads(text.split("```json\n", 1)[1].split("```", 1)[0])
        self.assertEqual(schema["required"], ["result", "checks", "evidence"])
        self.assertIn("head_sha", schema["properties"]["checks"]["items"]["required"])
        passed = schema["allOf"][0]["then"]["properties"]
        self.assertEqual(passed["checks"]["minItems"], 1)
        self.assertEqual(passed["checks"]["items"]["properties"]["result"]["const"], "passed")
        self.assertEqual(passed["evidence"]["minItems"], 1)
        self.assertEqual(schema["properties"]["evidence"]["items"]["format"], "uri")
        claude = (runtime / "claude.md").read_text(encoding="utf-8")
        self.assertIn("Android validation on a host without Android/KVM is manual", claude)


if __name__ == "__main__":
    unittest.main()
