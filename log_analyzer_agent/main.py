import os
from dotenv import load_dotenv
load_dotenv()
from crewai import Crew, Process
from agents import log_analyzer, issue_investigator, solution_specialist
from tasks import create_tasks
import datetime
import shutil
import sys

log_file_path = sys.argv[1]

with open(log_file_path, "r") as f:
    log_content = f.read()

print(f"Log file loaded — {len(log_content.splitlines())} lines found\n")

tasks = create_tasks(log_content)

crew = Crew(
    agents=[log_analyzer, issue_investigator, solution_specialist],
    tasks=tasks,
    process=Process.sequential,
    verbose=False,
)

result = crew.kickoff()

print("\n========== INCIDENT REPORT ==========")
print(result)
solution_text = result  
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"Solution_{timestamp}.txt"
with open(filename,"w") as file:
    file.write(str(solution_text))
DEST_DIR = "./LOGREPO"
os.makedirs(DEST_DIR, exist_ok=True)
destination_path = os.path.join(DEST_DIR, filename)
shutil.move(filename, DEST_DIR)
print(f"Moved '{filename}' to '{DEST_DIR}'")