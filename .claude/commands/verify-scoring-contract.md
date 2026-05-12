Use this command to verify the plugin still preserves the original CRM Dedupe Agent scoring contract.

Arguments from the user:

```text
$ARGUMENTS
```

Run:

```bash
python3 scripts/verify_original_scoring_contract.py --repo-root "$CRM_DEDUPE_AGENT_REPO"
```

If `CRM_DEDUPE_AGENT_REPO` is not set, ask for the path to a local checkout of `https://github.com/Andytoizer/crm-dedupe-agent`.

Expected output:

```text
OK: original scoring contract preserved
```
