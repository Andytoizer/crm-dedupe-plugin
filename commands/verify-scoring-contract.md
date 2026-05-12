---
description: Verify the plugin still preserves the original CRM Dedupe Agent scoring contract.
allowed-tools: ["Bash", "Read"]
---

# Verify Scoring Contract

User arguments:

```text
$ARGUMENTS
```

Run:

```bash
cd "${CLAUDE_PLUGIN_ROOT}" && python3 scripts/verify_original_scoring_contract.py
```

Expected output:

```text
OK: original scoring contract preserved
```

If output differs, the scoring contract has drifted — stop and report the diff to the user.
