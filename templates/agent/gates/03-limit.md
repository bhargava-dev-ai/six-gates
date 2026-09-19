# Gate III · Limit

**Who is allowed to write what?**

Agent: <working name> · Tier: <from Gate II>

A tool call is a form with blanks. For every blank, name who holds the pen, then enforce it at the tool boundary. This file mirrors `tools/catalog.yaml`, which is what the boundary actually reads. If they disagree, the catalog wins and this file is wrong.

## Tool catalog

| Tool | Argument | Pen | Source / validation / approval |
|---|---|---|---|
| <tool> | <arg> | application | `session.<field>` |
| <tool> | <arg> | human | approval token; standing limit <…> |
| <tool> | <arg> | model | type <…>, max <n> chars, allowlist <…> |

Pens:
- **application**: identifiers, agreed amounts, recipients, dates that trigger action. Injected by code. Model value ignored and logged.
- **model**: free text, classifications, rationale. Validated. Rendered, never executed.
- **human**: money, promises, access, deletion, precedent. No approval token, no call.

Tools reachable by the runtime but not in this catalog: <none, or how they are removed>

## Enforcement

| | |
|---|---|
| Location | `<repo/path/to/boundary>` |
| Unknown arguments | rejected and logged |
| Read scope | as the requesting user via <mechanism>, never a broader service account |

Signed: <security> · Date: <yyyy-mm-dd>

## Catalog changes

Any change here re-opens Gates III and V.

| Date | Change | Re-eval run | Signed |
|---|---|---|---|
