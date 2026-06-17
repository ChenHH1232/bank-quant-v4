from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def load_env() -> None:
    local_env = Path(__file__).with_name(".env")
    shared_env = Path(r"D:\hh\codex\daily\.env")

    if local_env.exists():
        load_dotenv(dotenv_path=local_env)
    elif shared_env.exists():
        load_dotenv(dotenv_path=shared_env)
    else:
        load_dotenv()


def main() -> None:
    load_env()

    api_key = getenv("DEEPSEEK_API_KEY")
    model = getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        raise RuntimeError(
            "Missing DEEPSEEK_API_KEY. Add it to v4/.env or D:/hh/codex/daily/.env."
        )

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a concise assistant for a quantitative research workflow.",
            },
            {
                "role": "user",
                "content": "Reply with one short sentence confirming the DeepSeek API connection is working.",
            },
        ],
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
