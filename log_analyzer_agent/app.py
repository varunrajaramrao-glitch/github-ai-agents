from fastapi import FastAPI
from pydantic import BaseModel
from crewai import Crew, Process
from agents import log_analyzer, issue_investigator, solution_specialist
from tasks import create_tasks

app = FastAPI()

class LogInput(BaseModel):

    log_content: str

@app.post("/analyze")

def analyze_log(input: LogInput):

    log_content = input.log_content
    tasks = create_tasks(log_content)

    crew = Crew(
                 agents=[log_analyzer, issue_investigator, solution_specialist],
                 tasks=tasks,
                 process=Process.sequential,
                 verbose=False,

    )

    result = crew.kickoff()
    return {"report": str(result)}