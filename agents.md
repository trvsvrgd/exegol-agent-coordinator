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
  - name: "Probe"
    role: "Test Executor"
    permissions:
      - "read"
      - "tests:run:requires-approval"
  - name: "Thrawn"
    role: "Cursor Liaison"
    permissions:
      - "read"
      - "cursor:prompt:requires-approval"
```
