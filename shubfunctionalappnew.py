import logging
import json
from fpdf import FPDF
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from azure.functions import HttpRequest, HttpResponse

def main(req: HttpRequest) -> HttpResponse:
    logging.info('Processing request for PDF generation.')

    try:
        # Parse the JSON input
        req_body = req.get_json()
        name = req_body.get("Name", "N/A")
        dob = req_body.get("DOB", "N/A")
        age = req_body.get("Age", "N/A")
        gender = req_body.get("Gender", "N/A")

        # Validate the required fields
        if not name or not dob or not age or not gender:
            return HttpResponse("Invalid input. All fields are required.", status_code=400)

        # Generate the PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"DOB: {dob}", ln=True)
        pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
        pdf.cell(200, 10, txt="Gender:", ln=True)
        pdf.rect(x=10, y=pdf.get_y(), w=5, h=5)  # Checkbox for Male
        pdf.cell(15, 10, txt="Male", ln=False)
        pdf.rect(x=40, y=pdf.get_y(), w=5, h=5)  # Checkbox for Female
        pdf.cell(15, 10, txt="Female", ln=True)

        # Save the PDF to a byte stream
        pdf_stream = BytesIO()
        pdf.output(pdf_stream)
        pdf_stream.seek(0)

        # Optional: Upload to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string("Your_Connection_String")
        container_name = "pdfs"
        blob_name = f"{name.replace(' ', '_')}.pdf"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        blob_client.upload_blob(pdf_stream, overwrite=True)

        # Return the PDF as a response
        pdf_stream.seek(0)  # Reset stream for return
        return HttpResponse(pdf_stream.read(), headers={"Content-Type": "application/pdf"})

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return HttpResponse(f"An error occurred: {str(e)}", status_code=500)
