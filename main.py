# main.py
import os
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse # <--- NEW IMPORT for clean error handling
from pydantic import BaseModel, Field
from typing import List

# --- NEW: Jinja2 Imports and Setup ---
from jinja2 import Environment, FileSystemLoader

# NOTE: Using the file name 'invoice_templatde.html' as seen in the folder screenshot.
template_env = Environment(
    # Searches for templates in the same directory as main.py
    loader=FileSystemLoader("."), 
    autoescape=False 
)
# Make sure the file name below matches your actual file name!
INVOICE_TEMPLATE = template_env.get_template("invoice_template.html")
# --------------------------------------

# --- WeasyPrint Windows Fix: START ---
# IMPORTANT: This block remains the same for WeasyPrint dependency setup.
try:
    # Ensure this path is correct for your system!
    gtk_path = Path('C:\\msys64\\mingw64\\bin') 
    if os.name == 'nt' and gtk_path.exists():
        os.environ['PATH'] = str(gtk_path) + os.pathsep + os.environ['PATH']
except Exception as e:
    print(f"Warning: Could not set GTK+ path: {e}")
# --- WeasyPrint Windows Fix: END ---

# This line should now work after setting the PATH above
from weasyprint import HTML, CSS 

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8001",
    "null" # Added for robustness when testing from local file system
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request body (No changes here)
class Item(BaseModel):
    model: str
    qty: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    unit: str = 'Pcs'

class InvoiceData(BaseModel):
    invoice_no: str
    date: str
    billed_to: str
    attention_to: str
    delivery_term: str
    validity_term: str
    delivery_time: str
    currency: str
    tax_rate: float = Field(..., ge=0, le=100)
    notes: str = ""
    contact_person: str = ""
    items: List[Item]

# --- MODIFIED FUNCTION TO USE JINJA2 ---
def get_invoice_template_html(data: InvoiceData):
    """
    Renders the invoice_templatde.html using Jinja2.
    """
    
    # 1. Process/Calculate Data in Python
    processed_items = []
    subtotal = 0
    
    for i, item in enumerate(data.items, 1):
        line_total = item.qty * item.unit_price
        subtotal += line_total
        
        # Prepare a dictionary for Jinja2 to easily access
        processed_items.append({
            "no": i,
            "model": item.model,
            "qty": item.qty,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "line_total_formatted": f"{line_total:.2f}", # Format here for clean template use
            "line_total": line_total
        })
        
    tax_amount = subtotal * (data.tax_rate / 100)
    grand_total = subtotal + tax_amount

    # 2. Render Template
    # We pass the calculated values and the raw data object to the template
    html_content = INVOICE_TEMPLATE.render(
        data=data,  # Pass the entire Pydantic object
        processed_items=processed_items, # Pass the list of processed items
        subtotal_formatted=f"{subtotal:.2f}",
        tax_amount_formatted=f"{tax_amount:.2f}",
        grand_total_formatted=f"{grand_total:.2f}",
    )
    
    return html_content
# -----------------------------------------


@app.options("/generate-invoice")
async def handle_options():
    # Return 204 No Content for a successful preflight response
    return Response(status_code=204)


@app.post("/generate-invoice")
async def generate_invoice_pdf(data: InvoiceData):
    """
    Generates a Proforma Invoice PDF from the provided data.
    """
    try:
        # 1. Get the HTML content
        html_content = get_invoice_template_html(data)

        # 2. Convert HTML to PDF using WeasyPrint
        pdf_bytes = HTML(string=html_content).write_pdf()

        # 3. Create the response
        headers = {
            'Content-Disposition': f'attachment; filename="invoice_{data.invoice_no}.pdf"'
        }
        
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf", 
            headers=headers
        )

    except Exception as e:
        error_message = str(e)
        
        # Dependency error check
        if "cannot load library" in error_message or "DLL load failed" in error_message:
             return JSONResponse(
                content={"detail": "WeasyPrint core dependency (GTK+) failed to load. Please ensure GTK+ is correctly installed and its 'bin' directory (e.g., C:\\msys64\\mingw64\\bin) is set in the 'gtk_path' variable on line 11."},
                status_code=500
            )
        
        # General error handling - Using JSONResponse for a dictionary response (Fixing the previous error)
        return JSONResponse(
            content={"detail": f"An unexpected error occurred during PDF generation: {e}"},
            status_code=500
        )
# To run: uvicorn main:app --reload