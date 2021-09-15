from pdf2image import convert_from_path
from flask import Flask,send_file, json, request, jsonify
import os
import urllib.request
from werkzeug.utils import secure_filename
import os.path

 
app = Flask(__name__)
 
app.secret_key = "caircocoders-ednalan"
 
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/')
def main():
    return 'Homepage'
 
@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'files[]' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
 
    files = request.files.getlist('files[]')
     
    errors = {}
    success = False
     
    for file in files:      
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True

            pages = convert_from_path(f'uploads/{filename}', 500)
            count=2
            for page in pages:
                if os.path.exists(f'uploads/{filename[:-4:]}.png'):
                    page.save(f'uploads/{filename[:-4:]}_{count}.png', 'PNG')
                    count += 1
                else:
                    page.save(f'uploads/{filename[:-4:]}.png', 'PNG')

        else:
            errors[file.filename] = 'File type is not allowed'
 
    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        resp = jsonify({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
 

@app.route('/download')
def downloadFile ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "uploads/"
    return send_file(path, as_attachment=True)


@app.route('/download_all')
def download_all ():
    dir = 'uploads'
    data_files = os.listdir (dir)
    data_files_fullpath = [os.path.join (dir, d) for d in data_files]
    for d in data_files_fullpath:
        print ('Download:' + d)
        send_file (d, as_attachment = True)
    return 'all files will be downloaded'


if __name__ == '__main__':
    app.run(debug=True)
