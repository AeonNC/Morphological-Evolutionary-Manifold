"""Typer CLI. Unaccepted stages fail closed instead of silently running.

Research Use Only. MEM is a computational research framework and is not validated
for clinical diagnosis, treatment selection, molecular profiling, clonal lineage
reconstruction, or minimal/measurable residual disease reporting.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from mem.constants import PROJECT_TITLE, PROJECT_VERSION, RESEARCH_DISCLAIMER, UPLOAD_WARNING
from mem.governance.fail_closed import FailClosedError, refuse_unimplemented, write_failure_artifact
from mem.governance.gates import GateRegistry, evaluate_g0_environment
from mem.governance.redteam import run_stage0_redteam
from mem.reporting.claim_linter import lint_or_fail
from mem.security.secrets import scan_secrets
from mem.utils.logging import get_logger, write_json

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help=f"{PROJECT_TITLE}\n\n{RESEARCH_DISCLAIMER}",
)
console = Console()
LOGGER = get_logger("mem.cli")

LATER_STAGE_COMMANDS = {
    "acquire-data": "1",
    "audit-data": "1",
    "build-manifest": "1",
    "find-duplicates": "1",
    "split-data": "1",
    "lock-split": "1",
    "train-detector": "3",
    "evaluate-detector": "3",
    "extract-patches": "3",
    "pretrain": "4",
    "finetune": "4",
    "calibrate": "4",
    "extract-embeddings": "4",
    "run-topology": "6",
    "build-mixtures": "7",
    "train-anomaly": "7",
    "evaluate": "5",
    "build-knowledge-graph": "8",
    "make-figures": "9",
    "build-report": "9",
    "launch-demo": "10",
}


def _closed(action) -> None:
    try:
        action()
    except FailClosedError as exc:
        LOGGER.error("%s: %s", exc.code, exc)
        raise typer.Exit(code=1) from exc


def _output_dir(value: Optional[Path]) -> Path:
    path = value or Path("outputs")
    path.mkdir(parents=True, exist_ok=True)
    return path


def _banner() -> None:
    console.print(f"[bold]{PROJECT_TITLE}[/bold]")
    console.print(f"[yellow]{RESEARCH_DISCLAIMER}[/yellow]")
    console.print(f"version={PROJECT_VERSION}")


@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(None, "--config", help="YAML config path."),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Artifact directory."),
    seed: Optional[int] = typer.Option(None, "--seed", help="RNG seed."),
    device: Optional[str] = typer.Option(None, "--device", help="cpu|cuda. Unused in Stage 0 modeling."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Describe actions without writing models."),
) -> None:
    """MEM research CLI. Fail closed. Research use only."""
    ctx.ensure_object(dict)
    ctx.obj = {
        "config": config,
        "output_dir": _output_dir(output_dir),
        "seed": seed,
        "device": device,
        "dry_run": dry_run,
    }
    if ctx.invoked_subcommand:
        _banner()


def _register_later_commands() -> None:
    for command, stage in LATER_STAGE_COMMANDS.items():

        def _factory(cmd: str = command, stg: str = stage) -> None:
            @app.command(cmd)
            def _cmd(
                ctx: typer.Context,
                config: Optional[Path] = typer.Option(None, "--config"),
                output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
                seed: Optional[int] = typer.Option(None, "--seed"),
                device: Optional[str] = typer.Option(None, "--device"),
                dry_run: bool = typer.Option(False, "--dry-run"),
            ) -> None:
                out = output_dir or ctx.obj["output_dir"]
                _closed(lambda: refuse_unimplemented(cmd, stg, out))

            _cmd.__doc__ = (
                f"Stage {stg} command. Disabled until that stage is accepted. {RESEARCH_DISCLAIMER}"
            )

        _factory()


_register_later_commands()


@app.command("setup-colab")
def setup_colab(
    ctx: typer.Context,
    output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
) -> None:
    """Write a Colab setup note. Does not download datasets or checkpoints."""
    out = output_dir or ctx.obj["output_dir"]
    note = {
        "disclaimer": RESEARCH_DISCLAIMER,
        "upload_warning": UPLOAD_WARNING,
        "instructions": [
            "Use notebooks/00_colab_setup.ipynb.",
            "Install requirements-stage0.txt first on CPU runtime.",
            "Do not upload patient-identifiable or clinical data.",
            "Persist artifacts to Google Drive only after privacy-scan PASS.",
            "Full GPU training is Stage 4+ and remains blocked.",
        ],
        "status": "STAGE0_ONLY",
    }
    path = out / "audits" / "colab_setup.json"
    write_json(path, note)
    console.print(f"Wrote {path}")


@app.command("claim-lint")
def claim_lint(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(None, "--config"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
    root: Path = typer.Option(Path("."), "--root"),
) -> None:
    """Scan documentation and code for prohibited unsupported scientific claims."""
    out = output_dir or ctx.obj["output_dir"]
    exceptions = Path("configs/claims/exceptions.yaml")
    exceptions_arg = exceptions if exceptions.exists() else None
    holder: dict = {}

    def _run() -> None:
        holder["result"] = lint_or_fail(root, out, exceptions_path=exceptions_arg)

    _closed(_run)
    result = holder["result"]
    console.print(
        f"claim-lint status={result.status} files={result.scanned_files} blocking={len(result.blocking_hits)}"
    )


@app.command("privacy-scan")
def privacy_scan_cmd(
    ctx: typer.Context,
    output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
    root: Path = typer.Option(Path("tests/fixtures/synthetic"), "--root"),
) -> None:
    """Scan a directory for identifier-like patterns. Default: synthetic fixtures only."""
    from mem.privacy.scanner import scan_paths

    out = output_dir or ctx.obj["output_dir"]
    files = [p for p in root.rglob("*") if p.is_file()]
    holder: dict = {}
    _closed(lambda: holder.update(result=scan_paths(files, out, fail_on_hit=True)))
    result = holder["result"]
    console.print(f"privacy-scan status={result.status} files={result.scanned_files}")


@app.command("validate-provenance")
def validate_provenance_cmd(
    ctx: typer.Context,
    output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
    metadata: Path = typer.Option(
        Path("data/raw/_templates/SOURCE_METADATA.template.json"),
        "--metadata",
    ),
) -> None:
    """Validate SOURCE_METADATA.json. Template files are expected to remain unapproved."""
    from mem.governance.provenance import load_source_metadata

    out = output_dir or ctx.obj["output_dir"]
    _closed(lambda: load_source_metadata(metadata, out))


@app.command("run-redteam")
def run_redteam(
    ctx: typer.Context,
    output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
) -> None:
    """Run Stage 0 adversarial tests against synthetic fixtures only."""
    out = output_dir or ctx.obj["output_dir"]
    holder: dict = {}
    _closed(lambda: holder.update(payload=run_stage0_redteam(Path("."), out, Path("tests/fixtures/adversarial"))))
    console.print(f"redteam status={holder['payload']['status']}")


@app.command("verify-release")
def verify_release(
    ctx: typer.Context,
    output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
) -> None:
    """Release gate. Stage 0 cannot produce PASS; remaining gates are NOT_STARTED."""
    out = output_dir or ctx.obj["output_dir"]
    registry = GateRegistry()
    gate_path = out / "audits" / "gates.json"
    if gate_path.exists():
        registry = GateRegistry.load(gate_path, out)
    blocked_reasons = [
        f"{gate_id}={registry.records[gate_id].status}"
        for gate_id in registry.records
        if registry.records[gate_id].status not in {"PASS", "PASS WITH DOCUMENTED LIMITATIONS"}
    ]
    write_json(
        out / "audits" / "release_status.json",
        {
            "disclaimer": RESEARCH_DISCLAIMER,
            "status": "BLOCKED",
            "reasons": blocked_reasons or ["Stage 0 does not authorize a research release."],
            "gates": registry.to_dict()["gates"],
        },
    )
    write_failure_artifact(
        out,
        code="RELEASE_BLOCKED",
        message="Final release is BLOCKED. Stage 0 is governance-only.",
        repair="Complete Stages 1–10 and all gates G0–G10 before any research release.",
        stage="G10",
    )
    raise typer.Exit(code=1)


@app.command("verify-g0")
def verify_g0(
    ctx: typer.Context,
    output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
) -> None:
    """Evaluate environment integrity for Stage 0 modules."""
    out = output_dir or ctx.obj["output_dir"]

    def _run() -> None:
        python_ok = sys.version_info >= (3, 10)
        required = {}
        for name, import_name in (
            ("pydantic", "pydantic"),
            ("yaml", "yaml"),
            ("typer", "typer"),
            ("PIL", "PIL"),
            ("torch", "torch"),
            ("ultralytics", "ultralytics"),
            ("gudhi", "gudhi"),
        ):
            try:
                __import__(import_name)
                required[name] = True
            except Exception:
                required[name] = False
        result = evaluate_g0_environment(
            output_dir=out,
            python_ok=python_ok,
            required_modules=required,
            unpinned_dependencies=[],
        )
        registry = GateRegistry()
        registry.set_status("G0", result["status"], output_dir=out, notes="; ".join(result["notes"]))
        registry.save(out / "audits" / "gates.json")
        write_json(out / "audits" / "g0.json", result)
        console.print(f"G0 status={result['status']}")
        scan_secrets(Path("."), out, fail_on_hit=True)

    _closed(_run)


def run() -> None:
    try:
        app()
    except FailClosedError as exc:
        LOGGER.error("%s: %s", exc.code, exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    run()
