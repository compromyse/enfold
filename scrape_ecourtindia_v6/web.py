import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)

# Directory where PDFs are stored
PDF_DIRECTORY = './pdf'

@app.route('/pdf/<filename>')
def view_pdf(filename):
    """
    Route to view a PDF file from the specified directory.
    
    Args:
        filename (str): Name of the PDF file to display
    
    Returns:
        PDF file or 404 error if file doesn't exist
    """
    try:
        # Ensure the filename is safe and exists
        if not filename.endswith('.pdf'):
            abort(400, description="Invalid file type. Only PDF files are allowed.")
        
        # Check if the file exists in the PDF directory
        filepath = os.path.join(PDF_DIRECTORY, filename)
        if not os.path.exists(filepath):
            abort(404, description="PDF file not found")
        
        # Send the PDF file
        return send_from_directory(PDF_DIRECTORY, filename, as_attachment=False)
    
    except Exception as e:
        abort(500, description=f"Internal server error: {str(e)}")

@app.route('/pdf')
def list_pdfs():
    """
    Route to list all available PDF files in the directory.
    
    Returns:
        HTML page with list of PDFs or error message
    """
    try:
        # Get list of PDF files in the directory
        pdf_files = [f for f in os.listdir(PDF_DIRECTORY) if f.endswith('.pdf')]
        
        # Create a simple HTML response with links to PDFs
        pdf_links = "\n".join([
            f'<li><a href="/pdf/{file}">{file}</a></li>' 
            for file in pdf_files
        ])
        
        return f"""
        <html>
            <head><title>PDF Viewer</title></head>
            <body>
                <h1>Available PDFs</h1>
                <ul>{pdf_links}</ul>
            </body>
        </html>
        """
    
    except Exception as e:
        abort(500, description=f"Error listing PDFs: {str(e)}")

if __name__ == '__main__':
    # Ensure PDF directory exists
    os.makedirs(PDF_DIRECTORY, exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=True)
