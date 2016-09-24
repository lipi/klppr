from flask import Flask
from flask import request

app = Flask(__name__)
FILENAME = 'address.txt'


@app.route("/ip/", methods=['GET', 'POST'])
def ip_address():
    if 'POST' == request.method:
        try:
            with open(FILENAME, 'wb') as f:
                addr = request.form.get('addr')
                f.write(addr)
                return ''
        except IOError:
            return 'Failed to store IP address\n'
    else:
        try:
            with open(FILENAME, 'rb') as f:
                return f.read()
        except IOError:
            return ''


