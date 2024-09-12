import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from dbos import DBOS
from dbos.dbos import WorkflowStatus

config = {
    "name": "moonlight_nucleus",
    "language": "python",
    "database": {
        "hostname": "localhost",
        "port": 5432,
        "username": "postgres",
        "password": os.environ["PGPASSWORD"],
        "app_db_name": "moonlight_nucleus",
    },
    "telemetry": {
        "logs": {
            "logLevel": "INFO",
        }
    },
    "env": {},
}

app = FastAPI()
DBOS(fastapi=app, config=config)


@app.get("/greeting/{name}")
@DBOS.workflow()
def example_workflow(name: str) -> str:
    DBOS.logger.info(f"Received a greeting request for {name} ({DBOS.workflow_id}).")


@app.get("/status/{wfid}")
async def status(wfid: str) -> WorkflowStatus | None:
    status = await DBOS.get_workflow_status(wfid)
    return status


@app.get("/sync-status/{wfid}")
def status(wfid: str) -> WorkflowStatus | None:
    status = DBOS.get_workflow_status(wfid)
    return status


@app.get("/")
async def readme() -> HTMLResponse:
    wf = DBOS.start_workflow(example_workflow, "dbos")
    readme = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Welcome to DBOS!</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="font-sans text-gray-800 p-6 max-w-2xl mx-auto">
            <h1 class="text-xl font-semibold mb-4">Welcome to DBOS!</h1>
            <p>
                Started Workflow: 
                <a href="status/{wf.workflow_id}" class="text-blue-600 hover:underline">Status</a> /
                <a href="sync-status/{wf.workflow_id}" class="text-blue-600 hover:underline">Sync Status</a>
            </p>
        </body>
        </html>
        """
    return HTMLResponse(readme)
