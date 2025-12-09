import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import uuid
from whatsapp_generator import WhatsAppLinkGenerator
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Dictionary to store background tasks
background_tasks = {}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

def run_background_task(task_id, file_path, message, is_url=False):
    """Run the WhatsApp link generation in the background"""
    try:
        # Update task status
        background_tasks[task_id] = {
            'status': 'Processing',
            'progress': 0,
            'message': 'Starting to process the file...',
            'result_file': None,
            'error': None
        }
        
        # Initialize the generator
        generator = WhatsAppLinkGenerator()
        
        # Process the data
        background_tasks[task_id]['progress'] = 25
        background_tasks[task_id]['message'] = 'Reading and processing the data...'
        
        df, phone_col, email_col, name_col = generator.process_data(file_path, message, is_url)
        
        # Save the output file
        background_tasks[task_id]['progress'] = 75
        background_tasks[task_id]['message'] = 'Generating output file...'
        
        output_filename = f"whatsapp_links_{task_id}.xlsx"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        if generator.save_to_excel(df, output_path):
            background_tasks[task_id]['status'] = 'Completed'
            background_tasks[task_id]['progress'] = 100
            background_tasks[task_id]['message'] = 'Process completed successfully!'
            background_tasks[task_id]['result_file'] = output_path
            background_tasks[task_id]['columns'] = {
                'phone': phone_col,
                'email': email_col,
                'name': name_col
            }
        else:
            background_tasks[task_id]['status'] = 'Failed'
            background_tasks[task_id]['error'] = 'Failed to save the output file'
    except Exception as e:
        background_tasks[task_id]['status'] = 'Failed'
        background_tasks[task_id]['error'] = str(e)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process it"""
    # Check if a file was uploaded
    if 'file' not in request.files and 'url' not in request.form:
        flash('No file or URL provided')
        return redirect(request.url)
    
    message = request.form.get('message', '')
    if not message:
        flash('No message provided')
        return redirect(request.url)
    
    # Create a unique task ID
    task_id = str(uuid.uuid4())
    
    # Check if it's a URL or file upload
    if 'url' in request.form and request.form['url']:
        url = request.form['url']
        # Start background processing
        thread = threading.Thread(
            target=run_background_task,
            args=(task_id, url, message, True)
        )
        thread.daemon = True
        thread.start()
    else:
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save the uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
            file.save(file_path)
            
            # Start background processing
            thread = threading.Thread(
                target=run_background_task,
                args=(task_id, file_path, message, False)
            )
            thread.daemon = True
            thread.start()
        else:
            flash('Invalid file type. Please upload CSV or Excel files.')
            return redirect(request.url)
    
    return redirect(url_for('task_status', task_id=task_id))

@app.route('/status/<task_id>')
def task_status(task_id):
    """Check the status of a background task"""
    if task_id not in background_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(background_tasks[task_id])

@app.route('/download/<task_id>')
def download_file(task_id):
    """Download the result file"""
    if task_id not in background_tasks:
        flash('Task not found')
        return redirect(url_for('index'))
    
    task = background_tasks[task_id]
    if task['status'] != 'Completed' or not task['result_file']:
        flash('File not ready for download')
        return redirect(url_for('index'))
    
    return send_file(
        task['result_file'],
        as_attachment=True,
        download_name=f"whatsapp_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

@app.route('/task/<task_id>')
def task_page(task_id):
    """Render the task status page"""
    if task_id not in background_tasks:
        flash('Task not found')
        return redirect(url_for('index'))
    
    return render_template('task.html', task_id=task_id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)