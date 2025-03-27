import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)

PDF_DIRECTORY = './pdf'

@app.route('/pdf/<filename>')
def view_pdf(filename):
    try:
        if not filename.endswith('.pdf'):
            abort(400, description="Invalid file type. Only PDF files are allowed.")
        
        filepath = os.path.join(PDF_DIRECTORY, filename)
        if not os.path.exists(filepath):
            abort(404, description="PDF file not found")
        
        return send_from_directory(PDF_DIRECTORY, filename, as_attachment=False)
    
    except Exception as e:
        abort(500, description=f"Internal server error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
