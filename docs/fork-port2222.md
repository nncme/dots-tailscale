# Owner fork: unprivileged SSH on port 2222

## Provenance and scope

This is an intentionally modified `nncme/dots-tailscale` bundle based on
`632d12a127253b33cdf35d9a132aef3aaf4df5fd`, not an unmodified upstream release.
Its package version is `0.7.0-nncme-port2222`; the official Tailscale runtime
baseline remains **1.104.4**. `scripts/source_manifest.py` regenerates the four
source hashes from this reviewed modified bundle; no baseline guard is removed.

This narrow fresh-install variant fixes SSH at **2222**. It changes the installer
preflight, generated OpenSSH configuration, startup banner probe, and package
update listener/readiness checks together. It does not change the kernel's
unprivileged-port threshold, capabilities, routing, tailnet policy, or authentication.
OpenSSH remains loopback-only and public-key-only; Tailscale SSH remains disabled.

With `ip_unprivileged_port_start=1024`, port 22 is unavailable to the ordinary
user but 2222 is eligible. A conflicting listener or other runtime restriction
can still prevent startup. Official Tailscale v1.104.4 userspace forwarding
[preserves the destination port when forwarding to loopback](https://github.com/tailscale/tailscale/blob/v1.104.4/wgengine/netstack/netstack.go#L1773-L1778).
After separately authorized installation/enrollment and independent host-key
verification, the client command is:

```bash
ssh -p 2222 -o StrictHostKeyChecking=yes -i /path/to/client_private_key agent@<tailscale-ip>
```

Tailnet access policy must authorize only intended clients to this node on TCP
2222. No public Internet exposure or Tailscale Serve/Funnel is required.

## Deployment boundaries

- Use the complete source bundle from the reviewed owner-fork commit, not the
  upstream release download/clone commands elsewhere in the inherited docs.
- Use a private `DOTS_TS_DIR` inside an authorized writable workspace. The
  default `/workspace/.dots-tailscale` is not assumed writable or persistent.
- This is **not** an in-place migration of an existing port-22 installation.
  Differing installed configuration is deliberately refused; do not remove
  existing identity files or force replacement. Design/review migration separately.
- Automatic package updates are off. The inherited manual updater still targets
  `abruption/dots-tailscale`; do not apply an upstream release over this fork
  without reviewing port compatibility, because it may restore port-22 behavior.
- Installation generates persistent CA and SSH host keys. Source staging and
  offline validation do not authorize that step, enrollment, or live listeners.
- Network access must be authorized independently. The inherited shim is not
  permission to bypass an allowlist, and no approved working transport is claimed.
- The inherited translated usage guides describe upstream port 22; use this
  fork-specific page for the port difference.

## Validation

Offline selected suite: `test_fork_ssh_port`, `test_install_helpers`,
`test_package_version`, `test_startup_readiness`, `test_update_apply`.
These use mocked network/runtime operations and inert existing identity fixtures.
The new tests cover threshold 1024/2222 acceptance, 2223 rejection, matching
loopback configuration/probes, and mocked package-update readiness on 2222.
Installer tests verify generated configuration while preserving inert keys.

Also run `bash -n tailscale-setup.sh` and
`python3 scripts/source_manifest.py --check`.

This is not a live Tailscale/SSH connection test. No key-generation/onboarding
tests, real SSH listener, tailnet enrollment, or platform network probe are
required by this selected validation. Actual external strict-host-key SSH and
persistence remain unverified until a separately approved deployment.
