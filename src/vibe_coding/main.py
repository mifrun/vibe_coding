from __future__ import annotations

import argparse
import os

from vibe_coding.crew import build_crew


def run() -> None:
    task = os.getenv("TASK", "Проверь проект и кратко опиши его состояние.")
    crew = build_crew(task=task)
    result = crew.kickoff(inputs={"user_task": task})
    print(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the CrewAI coding team.")
    parser.add_argument("task", nargs="?", help="Task for the CrewAI team.")
    parser.add_argument("--model", default=None, help="Override OPENAI_MODEL.")
    parser.add_argument("--quiet", action="store_true", help="Disable verbose CrewAI logs.")
    args = parser.parse_args()

    task = args.task or os.getenv("TASK")
    if not task:
        parser.error("Provide a task argument or TASK environment variable.")

    crew = build_crew(task=task, model=args.model, verbose=not args.quiet)
    result = crew.kickoff(inputs={"user_task": task})
    print("\n=== FINAL RESULT ===")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
