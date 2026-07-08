from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Crew, Process
from agents import log_analyzer, issue_investigator, solution_specialist
from tasks import create_tasks
import logging
import time
import uuid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

class LogInput(BaseModel):
    log_content: str

@app.post("/analyze")
def analyze_log(input: LogInput):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    logger.info(f"[{request_id}] New analysis request received - content length: {len(input.log_content)} chars")
    
    if not input.log_content.strip():
        logger.warning(f"[{request_id}] Empty log content received")
        raise HTTPException(
            status_code=400,
            detail="Log content cannot be empty. Please provide error log text."
        )
    
    try:
        log_content = input.log_content
        tasks = create_tasks(log_content)
        crew = Crew(
            agents=[log_analyzer, issue_investigator, solution_specialist],
            tasks=tasks,
            process=Process.sequential,
            verbose=False,
        )
        result = crew.kickoff()
        duration = time.time() - start_time
        logger.info(f"[{request_id}] Analysis complete in {duration:.2f}s")
        return {"report": str(result)}
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[{request_id}] Analysis failed after {duration:.2f}s - Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")
