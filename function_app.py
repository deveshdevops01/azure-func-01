import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Route + Blob output binding
@app.route(route="Function1HttptoBlob")
@app.blob_input(
    arg_name="inputblob",
    path="container1/data.txt",   # fixed blob name (non-dynamic)
    connection="AzureWebJobsStorage"
)
def Function1HttptoBlob(req: func.HttpRequest, inputblob: str) -> func.HttpResponse:

    logging.info('Python HTTP trigger function processed a request.')

    

    # Return normal HTTP response to the caller
    return func.HttpResponse(
        f"triggered successfully, content : \n\n{inputblob}", status_code=200
        )

# -------------------------------
# Function 2: Write to container2/write.txt
# -------------------------------

@app.route(route="WriteFileToBlob")
@app.blob_output(
    arg_name="outputblob",
    path="container2/write.txt",   # fixed blob name (non-dynamic)
    connection="AzureWebJobsStorage"
)
def WriteFileToBlob(req: func.HttpRequest, outputblob: func.Out[str]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function to write a file executed.')

     # Get content from query or body
    content = req.params.get("content")
    if not content:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        content = req_body.get("content", "Hello from WriteFileToBlob!")

    # Write into container2/write.txt
    outputblob.set(content)


    return func.HttpResponse(
        f"File 'write.txt' written successfully to container2 with content:\n\n{content}",
        status_code=200
    )


# -------------------------------
# Function 3: Create container3 and upload PDF
# -------------------------------
@app.route(route="UploadPdfToContainer3")
def UploadPdfToContainer3(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function to create container3 and upload PDF executed.')

    # Get storage connection string from local.settings.json
    connect_str = os.getenv("AzureWebJobsStorage")

    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create container3 if not exists
    container_name = "container3"
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
        logging.info(f"Container '{container_name}' created successfully.")
    except Exception as e:
        logging.info(f"Container '{container_name}' already exists or error: {e}")

    # Get file content (PDF) from request body
    try:
        file_bytes = req.get_body()
        if not file_bytes:
            return func.HttpResponse("No file data found in request body.", status_code=400)
    except Exception as e:
        return func.HttpResponse(f"Error reading request body: {e}", status_code=400)

    # File name (optional: allow passing in query string)
    filename = req.params.get("filename", "sample.pdf")

    # Upload file to container3
    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(file_bytes, overwrite=True)

    return func.HttpResponse(
        f"PDF file '{filename}' uploaded successfully to container '{container_name}'.",
        status_code=200
    )