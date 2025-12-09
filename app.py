import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from whatsapp_generator import WhatsAppLinkGenerator
from datetime import datetime

app = Flask(__name__)
# Use a consistent secret key for sessions, ideally from env var, but this is fine for now
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process it synchronously"""
    # Check if a file was uploaded
    if 'file' not in request.files and 'url' not in request.form:
        flash('No file or URL provided')
        return redirect(request.url)
    
    message = request.form.get('message', '')
    if not message:
        flash('No message provided')
        return redirect(request.url)
    
    try:
        generator = WhatsAppLinkGenerator()
        df = None
        phone_col, email_col, name_col = None, None, None

        # Check if it's a URL or file upload
        if 'url' in request.form and request.form['url']:
            url = request.form['url']
            df, phone_col, email_col, name_col = generator.process_data(url, message, is_url=True)
            original_filename = "data_from_url"
        else:
            file = request.files['file']
            if file.filename == '':
                flash('No file selected')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Use tempfile to save upload to handle Vercel's ephemeral FS optimally
                fd, file_path = tempfile.mkstemp(suffix=os.path.splitext(filename)[1])
                os.close(fd)
                file.save(file_path)
                
                try:
                    df, phone_col, email_col, name_col = generator.process_data(file_path, message, is_url=False)
                finally:
                    # Clean up the input file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                original_filename = os.path.splitext(filename)[0]
            else:
                flash('Invalid file type. Please upload CSV or Excel files.')
                return redirect(request.url)

        # Generate output
        output_filename = f"whatsapp_links_{original_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        if generator.save_to_excel(df, output_path):
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )


    except Exception as e:
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)