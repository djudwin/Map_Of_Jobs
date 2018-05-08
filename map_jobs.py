import os
import re
import builtins
builtins.unicode = str
# We'll render HTML templates and access data sent by POST using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, jsonify, redirect, session, url_for, send_from_directory
from flask_bower import Bower
from flask_triangle import Triangle
from werkzeug import secure_filename

# Triangle is very important and fixes the Angular / Flask {} issue; 

# Initialize the Flask application
app = Flask(__name__)
Bower(app)
Triangle(app)

# Home page
@app.route('/')
def main():
	return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081,debug=True)
