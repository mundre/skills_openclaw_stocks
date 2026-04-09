# Tests

## Minimal round-flow test
Run:

```bash
bash tests/test_round_flow.sh
```

Purpose:
- verify the sample round block includes required fields
- verify applied patches include a `PATCH_MANIFEST`
- verify a `stop` signal does not coexist with an unapplied proposed patch

## Weak-model shortcut fixture
Run:

```bash
bash tests/test_weak_model_shortcut.sh
```

Purpose:
- verify the simplified weak-model shortcut round still emits the minimum resumable state
