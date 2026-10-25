# Native probe ownership review

Research only. Windows private template capture remains disabled. This helper
creates zero-byte files with delete-on-close in a dedicated protected fixture.
It is not a persistent writer or a production security boundary.

## Findings and scope

Starting point: main b7d9458f0504a81267cbce3a0767a165ef4055f9 (merged PR #82).
Open related drafts #54 and #60 were inspected. #54 also injects its failure
after FileStream disposal; #60 concerns rename timing and does not establish
all-path cleanup. Neither draft is required or merged by this change.

The previous postcreate marker ran after the stream had closed its child
handle. It therefore did not exercise a failure with a live child handle.
WindowsIdentity.GetCurrent() results also were not disposed explicitly,
leaving token lifetime to finalization and complicating handle measurements.

The native error matrix and longest resource runner now compile one shared
NtOwnershipProbe.cs. Older standalone research snapshots remain unchanged;
these fixes must not be assumed to apply to every historical probe.

## Ownership

| Resource | Owner and release |
| --- | --- |
| Parent CreateFileW handle | Lexical using scope spans validation and the synchronous NtCreateFile call. The raw RootDirectory value is borrowed only within this scope, never published or disposed concurrently. |
| WindowsIdentity token | CurrentSid copies the SID string inside a using scope. |
| GetSecurityInfo descriptor | LocalFree in CheckParent finally after successful acquisition; owner/group/ACL pointers are borrowed interior pointers and are not freed separately. |
| UTF-16 name, UNICODE_STRING storage, child descriptor | Initially null, assigned inside try, individually freed with FreeHGlobal in finally, including partially initialized paths. |
| NtCreateFile output handle | Outer finally disposes any returned SafeFileHandle, including status rejection or failure before stream construction. |
| FileStream | using disposes stream and its supplied SafeFileHandle. The outer Dispose is idempotent; no second raw CloseHandle occurs. |

The UNICODE_STRING contains only a borrowed name pointer; StructureToPtr does
not allocate nested marshaled objects here. Its backing storage can be freed
directly. All three input buffers outlive the synchronous native call.

## Exercised paths and evidence

Executed on TREYS_DELL_RTX with 64-bit Windows PowerShell 5.1.26100.9549,
in a fresh isolated checkout and newly provisioned protected empty fixture.

- Native matrix: nine expected exceptions plus successful create/ACL validation
  and immediate deletion. New faults follow each of three unmanaged allocations,
  native child creation before FileStream construction, and stream construction.
  Original parent, precreate, postcreate and native-error cases remain.
- Exception matching uses the exact base-exception message. The invalid-root
  native case requires NTSTATUS 0xC000003B, not any arbitrary native failure.
- Long runner: 15 warm-up + 200 + 200 batches, nine operations each = 3,735.
  No orphan files. Warm/middle/end handles: 611 / 611 / 610.
  Private bytes: 75,669,504 / 77,254,656 / 77,225,984.
- Expanded Windows security gate: 8/8 suites passed, including the matrix.
- `python -m unittest services.pool_research.test_private_capture -v`:
  Windows refusal passed; three non-Windows tests skipped.
- `git diff --check`: passed.

Run from the repository root, with an absolute protected disposable fixture path:

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File services/pool_research/tests/test_nt_native_error_fault_matrix.ps1 -Directory <fixture>
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File services/pool_research/tests/test_nt_longrun_resource_measurements.ps1 -Directory <fixture>
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File services/pool_research/tests/run_windows_security_gate.ps1 -PrivateFixtureDirectory <fixture>
```

These are bounded observations, not proof of leak freedom. Resource snapshots
force GC, and injected post-allocation exceptions are not actual out-of-memory
or native allocator failures. Concurrent hostile mutation, process termination,
all NTSTATUS outcomes and production writer integration remain unvalidated.
No wallet, keys, daemon/network or production service was used or changed.
