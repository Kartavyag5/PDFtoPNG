from pdf2image import convert_from_path
from flask import Flask,send_file, json, request, jsonify
import os
import urllib.request
from werkzeug.utils import secure_filename
import os.path
import zipfile

 
app = Flask(__name__)
 
app.secret_key = "caircocoders-ednalan"
 
PDF_FOLDER = 'uploads/pdf'
PNG_FOLDER = 'uploads/png'
app.config['PDF_FOLDER'] = PDF_FOLDER

# this is for find the name of file while download zip
zipname = 'no file'

# you can only upload files in PDF format
ALLOWED_EXTENSIONS = set(['pdf'])
 
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

            #changes the zipname with the uploaded pdf name, global makes change for use it ,out of function
            global zipname
            zipname = filename
            
            file.save(os.path.join(app.config['PDF_FOLDER'], filename))
            success = True

            pages = convert_from_path(f'uploads/pdf/{filename}', 500)
            count=2
            os.mkdir(f'uploads/png/{filename[:-4:]}')
            for page in pages:
                if os.path.exists(f'uploads/png/{filename[:-4:]}/{filename[:-4:]}.png'):
                    page.save(f'uploads/png/{filename[:-4:]}/{filename[:-4:]}-{count}.png', 'PNG')
                    count += 1
                else:
                    page.save(f'uploads/png/{filename[:-4:]}/{filename[:-4:]}.png', 'PNG')

        else:
            errors[file.filename] = 'File type is not allowed'

    # this will create zipfile, write the png folder in it.
    
    zf = zipfile.ZipFile(f"uploads/zip/{filename[:-4:]}.zip", "w")
    for root,dirs,files in os.walk(f"uploads/png/{filename[:-4:]}"):
        for filename in files:
            zf.write(os.path.join(root, filename))
    zf.close()
 
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
 

# this route for download the file in zip format(with all png files)
@app.route('/download')
def download_zip():
    path = f'uploads/zip/{zipname[:-4:]}.zip'
    return send_file(path, as_attachment=True)


#if __name__ == '__main__':
    #app.run(debug=True)
