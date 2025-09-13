import azure.functions as func
import logging
import pyodbc
import os
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="DBselectOperation")
def DBselectOperation(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    connectionstring = os.environ["connectionstring"]
    conn = pyodbc.connect(connectionstring)
    cursor = conn.cursor()

    # Extract parameters from query
    name = req.params.get('name')
    topic = req.params.get('topic')

    # If not found, try request body
    if not name or not topic:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        if not name:
            name = req_body.get('name')
        if not topic:
            topic = req_body.get('topic')

    # Run query
    if name and topic:
        cursor.execute(
            "SELECT * FROM OnlineCourses WHERE Instructor = ? AND Topic = ?",
            (name, topic)
        )
    else:
        cursor.execute("SELECT * FROM OnlineCourses")

    records = cursor.fetchall()
    logging.info(records)

    # Convert to JSON serializable
    records_json = json.dumps([list(r) for r in records], indent=2)

    return func.HttpResponse(
        body=records_json,
        status_code=200,
        mimetype="application/json"
    )


# $env:PYTHON_PATH="C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe"
# func host start
