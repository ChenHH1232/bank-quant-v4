from pathlib import Path
import subprocess
import sys


PROMPT_FILES = [
    "601009_XSHG_2024_targeted_prompt.txt",
    "601009_XSHG_2025_targeted_prompt.txt",
    "600036_XSHG_2024_targeted_prompt.txt",
]


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    prompt_dir = base_dir / "deepseek_bank_indicator_targeted" / "prompts"
    output_dir = base_dir / "deepseek_bank_indicator_targeted" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    runner = base_dir.parent / "deepseek_task_runner.py"

    for idx, prompt_name in enumerate(PROMPT_FILES, start=1):
        prompt_path = prompt_dir / prompt_name
        if not prompt_path.exists():
            print(f"SKIP_MISSING {prompt_name}")
            continue
        output_path = output_dir / prompt_name.replace("_prompt.txt", "_result.txt")
        command = [
            sys.executable,
            str(runner),
            "targeted",
            "--task-file",
            str(prompt_path),
            "--max-output-tokens",
            "500",
        ]
        print(f"[{idx}/{len(PROMPT_FILES)}] {prompt_name}")
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output_path.write_text(result.stdout + ("\nSTDERR:\n" + result.stderr if result.stderr else ""), encoding="utf-8")
        print(f"saved -> {output_path.name}")


if __name__ == "__main__":
    main()
