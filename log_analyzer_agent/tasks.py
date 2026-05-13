from crewai import Task
from agents import log_analyzer, issue_investigator, solution_specialist

def create_tasks(log_content: str):

    analyze_task = Task(
        description=(
            f"Analyze this log file content:\n\n{log_content}\n\n"
            "Provide:\n"
            "1. Timeline of events\n"
            "2. List of all errors and warnings\n"
            "3. Severity assessment (Critical/High/Medium/Low)"
        ),
        expected_output=(
            "A structured summary with timeline, error list, and severity assessment."
        ),
        agent=log_analyzer,
    )

    investigate_task = Task(
        description=(
            "Based on the log analysis, investigate the root cause.\n"
            "Identify:\n"
            "1. Primary root cause\n"
            "2. Contributing factors\n"
            "3. Impact on the system\n"
            "4. Which services are affected"
        ),
        expected_output=(
            "A root cause analysis report with affected services and impact assessment."
        ),
        agent=issue_investigator,
        context=[analyze_task],  # ← explicitly pass Agent 1 output
    )

    solution_task = Task(
        description=(
            "Based on the root cause analysis, search the internet and provide solutions.\n"
            "Include:\n"
            "1. Immediate fix (what to do right now)\n"
            "2. Short term fix (next 24 hours)\n"
            "3. Long term fix (permanent solution)\n"
            "4. How to prevent this in future"
        ),
        expected_output=(
            "A clear incident resolution guide with immediate, short term, "
            "and long term fixes plus prevention steps."
        ),
        agent=solution_specialist,
        context=[analyze_task, investigate_task],  # ← explicitly pass both outputs
    )

    return [analyze_task, investigate_task, solution_task]