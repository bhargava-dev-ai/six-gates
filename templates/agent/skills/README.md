# Skills

Every file in this folder begins with a provenance header. A skill without one is inactive.

```
---
producer: human | agent
model: <model id, if agent-authored>
created: <yyyy-mm-dd>
triggering-case: <case id or escalation id, if agent-authored>
reviewed-by: <name>          # empty means inactive
reviewed-on: <yyyy-mm-dd>
owner: <name>
---
```

Agent-authored skills arrive as pull requests. Nothing becomes active until `reviewed-by` is filled in by a human.
