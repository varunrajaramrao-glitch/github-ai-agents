import os
from crewai import Agent, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
)

search_tool = SerperDevTool(
    api_key=os.getenv("SERPER_API_KEY")
)

log_analyzer = Agent(
    role="Log Analyzer",
    goal="Read and summarize log files clearly identifying all events, warnings and errors",
    llm=llm,
    backstory=(
        "You are an expert Site Reliability Engineer with 10 years of experience. "
        "You can read any log file and instantly summarize what happened, "
        "when it happened, and how severe it is."
    ),
)

issue_investigator = Agent(
    role="Issue Investigator",
    goal="Identify root cause of errors found in the log analysis",
    llm=llm,
    backstory=(
        "You are a senior backend engineer specializing in microservices and APIs. "
        "You dig deep into error patterns, identify root causes, "
        "and understand how failures cascade across distributed systems."
    ),
)

solution_specialist = Agent(
    role="Solution Specialist",
    goal="Research and provide actionable solutions for the identified issues",
    llm=llm,
    #tools=[search_tool],
    backstory=(
        "You are a solutions architect who specializes in fixing production incidents. "
        "You search the internet for the latest best practices and provide "
        "clear step-by-step fixes that an on-call engineer can action immediately."
    ),
)