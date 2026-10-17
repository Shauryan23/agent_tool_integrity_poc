"""Agent tool-argument integrity demo: simulated transport corruption.

No LLM, external services, or real tools are invoked. Python 3.9+.
This illustrates a failure mode; it does not reproduce IEC-Bench.
"""

import csv
import json
from collections import Counter

CASES = [
    ("plain", "reports/weekly.txt"),
    ("windows_path", r"C:\new\reports"),
    ("escaped_newline", r"literal\nsequence"),
    ("escaped_tab", r"column\tname"),
    ("regex", r"\d+\w+"),
]


def buggy_adapter(value: str) -> str:
    """Deliberately incorrect unescaping in a hypothetical adapter."""
    return (value.replace(r"\n", "\n")
                 .replace(r"\r", "\r")
                 .replace(r"\t", "\t"))


def identity_adapter(value: str) -> str:
    return value


ROUTES = [
    ("buggy_unchecked", buggy_adapter, False),
    ("buggy_guarded", buggy_adapter, True),
    ("json_guarded", identity_adapter, True),
]

rows = []
for case, intended in CASES:
    emitted = {"tool": "read_text", "arguments": {"path": intended}}
    # This JSON round trip preserves the argument in these examples.
    decoded = json.loads(json.dumps(emitted))
    for route, adapter, verify in ROUTES:
        received = adapter(decoded["arguments"]["path"])
        changed = received != intended
        status = "REFUSED" if verify and changed else "WOULD_EXECUTE"
        rows.append({
            "case": case,
            "route": route,
            "changed": changed,
            "status": status,
            "intended_repr": repr(intended),
            "received_repr": repr(received),
        })

with open("integrity_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print("Route              Changed   Refused   Would execute")
for route, _, _ in ROUTES:
    selected = [r for r in rows if r["route"] == route]
    counts = Counter(r["status"] for r in selected)
    print(f"{route:18} {sum(r['changed'] for r in selected):7}"
          f" {counts['REFUSED']:9} {counts['WOULD_EXECUTE']:15}")

print("\nChanged examples (intended -> received):")
for r in rows:
    if r["route"] == "buggy_unchecked" and r["changed"]:
        print(f"  {r['case']}: {r['intended_repr']} -> {r['received_repr']}")

assert sum(r["changed"] for r in rows if r["route"] == "buggy_unchecked") == 3
assert sum(r["status"] == "REFUSED" for r in rows if r["route"] == "buggy_guarded") == 3
assert not any(r["changed"] for r in rows if r["route"] == "json_guarded")
print("\nSaved: integrity_results.csv")
