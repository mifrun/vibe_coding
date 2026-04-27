from __future__ import annotations

import os
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from vibe_coding.tools import GitDiffTool, ListFilesTool, ReadFileTool, RunCommandTool, WriteFileTool


ROOT = Path(__file__).resolve().parents[2]


def build_llm_name(model: str) -> str:
    if "/" in model:
        return model
    return f"openai/{model}"


def configure_environment() -> str:
    load_dotenv(ROOT / ".env")
    if os.getenv("OPENAI_BASE_URL") and not os.getenv("OPENAI_API_BASE"):
        os.environ["OPENAI_API_BASE"] = os.environ["OPENAI_BASE_URL"]
    model = os.getenv("OPENAI_MODEL")
    if not model:
        raise RuntimeError("OPENAI_MODEL is not set.")
    return model


@CrewBase
class VibeCodingCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, model: str | None = None, verbose: bool = True) -> None:
        model_name = model or configure_environment()
        self.llm = build_llm_name(model_name)
        self.verbose = verbose

    @agent
    def project_manager(self) -> Agent:
        return Agent(config=self.agents_config["project_manager"], tools=[ListFilesTool(), ReadFileTool()], llm=self.llm, verbose=self.verbose)

    @agent
    def lead_analyst(self) -> Agent:
        return Agent(config=self.agents_config["lead_analyst"], tools=[ListFilesTool(), ReadFileTool()], llm=self.llm, verbose=self.verbose)

    @agent
    def system_analyst(self) -> Agent:
        return Agent(config=self.agents_config["system_analyst"], tools=[ListFilesTool(), ReadFileTool()], llm=self.llm, verbose=self.verbose)

    @agent
    def tech_lead(self) -> Agent:
        return Agent(config=self.agents_config["tech_lead"], tools=[ListFilesTool(), ReadFileTool()], llm=self.llm, verbose=self.verbose)

    @agent
    def developer(self) -> Agent:
        return Agent(
            config=self.agents_config["developer"],
            tools=[ListFilesTool(), ReadFileTool(), WriteFileTool(), RunCommandTool(), GitDiffTool()],
            llm=self.llm,
            verbose=self.verbose,
            max_iter=10,
        )

    @agent
    def qa(self) -> Agent:
        return Agent(
            config=self.agents_config["qa"],
            tools=[ListFilesTool(), ReadFileTool(), RunCommandTool(), GitDiffTool()],
            llm=self.llm,
            verbose=self.verbose,
            max_iter=7,
        )

    @task
    def plan_task(self) -> Task:
        return Task(config=self.tasks_config["plan_task"])

    @task
    def analysis_task(self) -> Task:
        return Task(config=self.tasks_config["analysis_task"])

    @task
    def system_plan_task(self) -> Task:
        return Task(config=self.tasks_config["system_plan_task"])

    @task
    def tech_review_task(self) -> Task:
        return Task(config=self.tasks_config["tech_review_task"])

    @task
    def implementation_task(self) -> Task:
        return Task(config=self.tasks_config["implementation_task"])

    @task
    def qa_task(self) -> Task:
        return Task(config=self.tasks_config["qa_task"])

    @task
    def summary_task(self) -> Task:
        return Task(config=self.tasks_config["summary_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=self.verbose,
        )


def build_crew(task: str, model: str | None = None, verbose: bool = True) -> Crew:
    return VibeCodingCrew(model=model, verbose=verbose).crew()
