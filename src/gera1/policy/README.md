# Policy and audit boundary

The local prototype now implements the gateway pattern described in [governance](../../../docs/GOVERNANCE.md):

- deny by default;
- scope grants to an actor, business and named capability;
- stop denied requests before the specialist reader runs;
- append authorization and completion events to a private JSONL audit log;
- block local-data reads when the authorization event cannot be audited;
- keep money/quantity values and local paths out of the audit summary; and
- read policy configuration once from a bounded regular non-symlink file using strict JSON.

The CLI actor comes from the trusted local policy file, not a request argument. This is a local bootstrap boundary, not hosted user authentication. A deployed front door must supply a verified principal from its identity system.
