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


if __name__ == "__main__":
    unittest.main()
