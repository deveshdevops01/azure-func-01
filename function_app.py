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
    cursor.execute('SELECT * FROM OnlineCourses')
    
    records = list(cursor.fetchall())
    print(records)
    logging.info(records)
    
    

    records = [tuple(records) for records in records]
    return_body = json.dumps(obj=records, indent=2)

    return func.HttpResponse(
    status_code=200,
    mimetype="application/json",
    body = return_body
)

# $env:PYTHON_PATH="C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe"
# func host start
