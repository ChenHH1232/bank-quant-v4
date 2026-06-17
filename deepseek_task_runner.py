import argparse
import sys
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def safe_print(text: str = "") -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace") + b"\n")


def load_env() -> None:
    local_env = Path(__file__).with_name(".env")
    shared_env = Path(r"D:\hh\codex\daily\.env")

    if local_env.exists():
        load_dotenv(dotenv_path=local_env)
    elif shared_env.exists():
        load_dotenv(dotenv_path=shared_env)
    else:
        load_dotenv()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a simple delegated task through DeepSeek and report usage."
    )
    parser.add_argument(
        "task",
        nargs="+",
        help="The task description to send to DeepSeek.",
    )
    parser.add_argument(
        "--task-file",
        default=None,
        help="Optional UTF-8 text file containing the full task prompt.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override. Defaults to DEEPSEEK_MODEL or deepseek-v4-flash.",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=400,
        help="Target output token budget for this delegated task.",
    )
    return parser


def main() -> None:
    load_env()

    api_key = getenv("DEEPSEEK_API_KEY")
    model = getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        raise RuntimeError(
            "Missing DEEPSEEK_API_KEY. Add it to v4/.env or D:/hh/codex/daily/.env."
        )

    args = build_parser().parse_args()
    selected_model = args.model or model
    if args.task_file:
        task_text = Path(args.task_file).read_text(encoding="utf-8")
    else:
        task_text = " ".join(args.task)

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a reliable assistant for simple, repetitive work. "
                "Complete the task directly and keep the answer concise. "
                "Always return a visible final answer, even if it is only one sentence."
            ),
        },
        {
            "role": "user",
            "content": task_text,
        },
    ]

    response = client.chat.completions.create(
        model=selected_model,
        max_tokens=args.max_output_tokens,
        messages=messages,
    )

    first_message = response.choices[0].message
    message = first_message.content or ""
    reasoning_message = getattr(first_message, "reasoning_content", None) or ""
    retried_for_empty_output = False

    if not message.strip() and not reasoning_message.strip():
        retried_for_empty_output = True
        response = client.chat.completions.create(
            model=selected_model,
            max_tokens=max(args.max_output_tokens * 2, 200),
            messages=messages
            + [
                {
                    "role": "assistant",
                    "content": "Your previous attempt produced no visible final answer.",
                },
                {
                    "role": "user",
                    "content": "Retry now and output only the final answer text.",
                },
            ],
        )
        first_message = response.choices[0].message
        message = first_message.content or ""
        reasoning_message = getattr(first_message, "reasoning_content", None) or ""

    visible_message = message.strip() or reasoning_message.strip()

    usage = getattr(response, "usage", None)
    completion_tokens = getattr(usage, "completion_tokens", None)
    prompt_tokens = getattr(usage, "prompt_tokens", None)
    total_tokens = getattr(usage, "total_tokens", None)

    safe_print("=== DeepSeek Result ===")
    safe_print(visible_message)
    safe_print()
    safe_print("=== Token Report ===")
    safe_print("Remaining tokens: not returned by DeepSeek API")
    safe_print(f"Target tokens: {args.max_output_tokens}")
    safe_print(f"Retried for empty output: {'yes' if retried_for_empty_output else 'no'}")
    safe_print(f"Used reasoning fallback: {'yes' if (not message.strip() and reasoning_message.strip()) else 'no'}")
    safe_print(
        "Actual tokens: "
        f"prompt={prompt_tokens if prompt_tokens is not None else 'not returned'}, "
        f"completion={completion_tokens if completion_tokens is not None else 'not returned'}, "
        f"total={total_tokens if total_tokens is not None else 'not returned'}"
    )


if __name__ == "__main__":
    main()
