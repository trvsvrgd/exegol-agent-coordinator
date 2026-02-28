# Agents

```yaml
agents:
  - name: "Vader"
    role: "Lead Orchestrator"
    permissions:
      - "read"
      - "write"
      - "git:commit"
  - name: "Maul"
    role: "Builder"
    permissions:
      - "read"
      - "write"
      - "git:commit:requires-approval"
```
