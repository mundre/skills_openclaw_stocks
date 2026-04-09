# Packaging Checklist

Before setting `PUBLISH_STATUS: Packaged`, confirm the archive includes:
- `SKILL.md`
- `references/modes.md`
- `references/skill-review-mode.md`
- `references/skill-classes.md`
- `references/round-output-contract.md`
- `references/failure-handling.md`
- `references/patch-discipline.md`
- `references/convergence-rules.md`
- `references/weak-model-guide.md`
- `references/validator-schema.md`
- `references/examples.md`
- `tests/test_round_flow.sh`
- `tests/test_weak_model_shortcut.sh`
- `tests/test_reference_alignment.sh`
- `tests/fixtures/sample-round-block.txt`
- `tests/fixtures/weak-model-shortcut-round.txt`
- `tests/README.md`

Release checks:
- `python3 skills/skill-creator-canonical/scripts/quick_validate.py skills/dual-thinking`
- `python3 skills/skill-creator-canonical/scripts/validate_weak_models.py skills/dual-thinking`
- `bash skills/dual-thinking/tests/test_round_flow.sh`
- `bash skills/dual-thinking/tests/test_weak_model_shortcut.sh`
- `bash skills/dual-thinking/tests/test_reference_alignment.sh`
