# AI Log Analyzer Agent
[![Deploy Log Analyzer](https://github.com/varunrajaramrao-glitch/github-ai-agents/actions/workflows/deploy.yml/badge.svg)](https://github.com/varunrajaramrao-glitch/github-ai-agents/actions/workflows/deploy.yml)

An AI-powered incident response system that automatically analyzes production error logs and generates precise, actionable resolution reports using a multi-agent architecture.

## The Problem It Solves

Production support engineers waste hours manually reading error logs, searching Google for generic answers, and piecing together fixes. This system automates that entire process — giving ops teams immediate, context-aware RCA and resolution steps they can actually implement.

## Who Is This For

- Production Support Engineers
- SRE and Operations Teams
- DevOps Engineers managing live systems

## How It Works

1. Send your error log content to the `/analyze` API endpoint
2. Three specialized AI agents process it sequentially:
   - **Log Analyzer** — reads and summarizes errors, warnings and severity
   - **Issue Investigator** — performs root cause analysis and identifies error patterns
   - **Solution Specialist** — generates immediate fixes, short-term workarounds and long-term preventive measures
3. Receive a structured incident resolution report as a response

## Why Not Just Google It

Google returns generic answers that may or may not apply to your specific error. This system uses specialized agents for each task — analysis, investigation, and resolution — producing precise, implementable output tailored to your exact log content.

## Tech Stack

- **CrewAI** — multi-agent orchestration
- **FastAPI** — REST API layer
- **Docker** — containerization
- **AWS EC2** — cloud deployment
- **Python** — core language

## Live API

The API is deployed and accessible at:

```
http://13.60.181.216:8000/docs
```

## API Usage

**Endpoint:** `POST /analyze`

**Request:**
```json
{
  "log_content": "ERROR: Connection timeout to OrderService at 03:45:22"
}
```

**Response:**
```json
{
  "report": "Incident Resolution Guide with immediate, short-term and long-term fixes..."
}
```
## Screenshots

### Live API on AWS EC2
![API Documentation](link-to-screenshot)
<img width="700" height="300" alt="image" src="https://github.com/user-attachments/assets/28bac1cc-82e4-4dc8-b3e5-967a5ed8bd30" />



### Sample Response
![Sample Response](link-to-screenshot)
<img width="700" height="300" alt="image" src="https://github.com/user-attachments/assets/de02b394-a3fa-44b3-9363-547174390ab6" />


## Run Locally with Docker

```bash
docker pull zxcrty/log-analyzer:v1

docker run -p 8000:8000 \
  -e GROQ_API_KEY="your-key" \
  -e SERPER_API_KEY="your-key" \
  zxcrty/log-analyzer:v1
```

Then open `http://localhost:8000/docs`

## Architecture

```
Error Log → FastAPI Endpoint → Log Analyzer Agent
                             → Issue Investigator Agent  
                             → Solution Specialist Agent
                             → Incident Resolution Report
```
## Future Enhancements
- File upload support for bulk log analysis
- Slack/email notification integration
- Log rotation and archiving
- Automated scheduling for periodic log analysis
- Authentication and rate limiting
