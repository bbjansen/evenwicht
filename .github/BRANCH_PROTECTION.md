# Branch Protection Setup

Run these commands after the initial push to configure branch protection
on GitHub. Requires the `gh` CLI with admin access.

## Protect main branch

```bash
gh api repos/bbjansen/evenwicht/branches/main/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Documentation checks",
      "Mathematical verification"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
```

## Branching strategy

```
main              ← stable, protected, deploys site
  └─ feature/*    ← new content or functionality
  └─ fix/*        ← errata and corrections
  └─ docs/*       ← documentation improvements
  └─ chore/*      ← maintenance and tooling
```

All changes go through pull requests. CI must pass before merge.
Direct pushes to `main` are blocked after initial setup.
