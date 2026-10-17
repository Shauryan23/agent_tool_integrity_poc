# Agent Tool Argument Integrity — Minimal POC

Inspired by *Do Tool Calls Execute as Intended? Measuring and Repairing Intent-Execution Correspondence in LLM Agents* (arXiv:2610.04375, 3 October 2026).

This is an **illustrative simulation**, not a reproduction of IEC-Bench, and does not test LangGraph, MCP, or any production agent framework. It performs no real tool calls.

## Architecture

Emitted structured tool arguments → JSON serialization/deserialization → simulated adapter → optional integrity check → `WOULD_EXECUTE` or `REFUSED` decision.

## Run

Requires Python 3.9+; no third-party dependencies.

```bash
python agent_tool_integrity_poc.py
```

It writes `integrity_results.csv` to the current working directory and prints a summary. The CSV included in this folder is a sample generated from the provided script.

## Results (5 deliberately chosen synthetic test cases)

| Route | Changed arguments | Refused calls | Calls that would execute |
| --- | ---: | ---: | ---: |
| Buggy adapter without check | 3 | 0 | 5 |
| Buggy adapter with equality check | 3 | 3 | 2 |
| JSON-preserving adapter with check | 0 | 0 | 5 |

The deliberately buggy adapter transforms the literal sequences `\\n`, `\\r`, and `\\t` into control characters. The example's integrity guard can reject changes because it retains the trusted original argument. Real tool adapters require end-to-end instrumentation, robust schemas, and execution-time checks to establish the meaning of a tool action.

