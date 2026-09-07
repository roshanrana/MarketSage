"""Run the offline evaluation and write metrics/headline.json.

    python -m marketsage_eval            # write headline, detail and contract fixtures
    python -m marketsage_eval --check    # exit 1 if the committed headline or fixtures are stale
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from marketsage_core.repo import repo_root
from marketsage_eval import api_eval, headline, retrieval_eval, scenarios, sentiment_eval
from marketsage_eval.fixtures import manifest

GO_TIMEOUT_SECONDS = 180


def collect(base: Path, skip_go: bool = False) -> dict[str, Any]:
    data_dir = base / "api"
    data_dir.mkdir(parents=True)
    with api_eval.seeded_client(data_dir) as api:
        responses = api_eval.run_tool_chain(api)
        # Audit is scored on the single replayed chain, before the timing loop adds rows.
        audit = api_eval.audit_report(data_dir, responses)
        run_id = responses[-1]["body"]["data"]["run_id"]
        latency = api_eval.latency_report(api, run_id)
    settings = api_eval.seeded_settings(base / "grounding")

    return {
        "fixtures": manifest(),
        "retrieval": retrieval_eval.run(),
        "sentiment": sentiment_eval.run(settings),
        "grounding": api_eval.grounding_report(settings),
        "contracts": api_eval.contracts_report(responses),
        "envelopes": api_eval.envelope_report(responses),
        "audit": audit,
        "scenarios": [
            asdict(o) | {"passed": o.passed} for o in scenarios.run_all(base / "scenarios")
        ],
        "latency": latency,
        "mcp_surface": None if skip_go else describe_mcp_surface(),
        "contract_fixtures": api_eval.pinned_fixtures(responses, data_dir),
    }


def describe_mcp_surface() -> dict[str, Any] | None:
    go = shutil.which("go")
    if go is None:
        return None
    gateway = repo_root() / "services" / "mcp-gateway-go"
    try:
        completed = subprocess.run(
            [go, "run", "./cmd/marketsage-mcp", "--describe"],
            cwd=gateway,
            capture_output=True,
            text=True,
            timeout=GO_TIMEOUT_SECONDS,
            check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"warning: could not describe the MCP surface: {exc}", file=sys.stderr)
        return None
    return json.loads(completed.stdout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    root = repo_root()
    parser.add_argument("--out", type=Path, default=root / "metrics" / "headline.json")
    parser.add_argument("--detail", type=Path, default=root / "metrics" / "eval-latest.json")
    parser.add_argument(
        "--fixtures-out", type=Path, default=root / "packages" / "contracts" / "fixtures"
    )
    parser.add_argument("--check", action="store_true", help="fail if committed outputs are stale")
    parser.add_argument("--skip-go", action="store_true", help="do not run the Go gateway")
    args = parser.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="marketsage-eval-") as tmp:
        results = collect(Path(tmp), skip_go=args.skip_go)

    fixtures = results.pop("contract_fixtures")
    card = headline.build(results)
    rendered = headline.render(card)

    if args.check:
        stale = []
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != rendered:
            stale.append(str(args.out))
        for name, content in fixtures.items():
            target = args.fixtures_out / name
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                stale.append(str(target))
        if stale:
            print("stale, run `npm run eval` and commit: " + ", ".join(stale))
            return 1
        print("metrics/headline.json and contract fixtures are current")
        return 0

    headline.write(card, args.out)
    args.detail.parent.mkdir(parents=True, exist_ok=True)
    args.detail.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    args.fixtures_out.mkdir(parents=True, exist_ok=True)
    for name, content in fixtures.items():
        (args.fixtures_out / name).write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote {args.out}, {args.detail} and {len(fixtures)} contract fixtures")
    for key, tile in card["kpis"].items():
        print(f"  {key}: {tile['value']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
