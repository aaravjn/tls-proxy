from flask import Flask, request, send_file
import hashlib

app = Flask(__name__)

@app.route('/certificate', methods=['GET'])
def get_issuer_ca():
    if 'hash' in request.args:
        hash = request.args['hash']
        with open('issuer-ca.crt', 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        if hash == file_hash:
            return "Hash is the same"
        else:
            return send_file('issuer-ca.crt')
    return send_file('issuer-ca.crt')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)