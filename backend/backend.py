from flask import Flask, request, jsonify
from backend.lib import cbc_decrypt, cbc_encrypt, ctr_encrypt, ctr_decrypt, ecb_encrypt, ecb_decrypt

app = Flask(__name__)

def validate_request_data(data, required_keys):
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        response = {"error": f"Missing keys in request: {', '.join(missing_keys)}"}
        return response, False
    return {}, True

@app.route('/encrypt/CBC', methods=['POST'])
def encrypt_cbc():
    data = request.json
    response, valid = validate_request_data(data, ['name', 'key', 'plaintext'])
    if not valid:
        return jsonify(response), 400

    name = data['name']
    key = data['key'].encode()
    plaintext = data['plaintext'].encode()
    iv = b"JEODB34DOlgSHuRP"
    ciphertext = cbc_encrypt(plaintext, key, iv)

    header = b"MODE:CBC\n"
    full_data = header + ciphertext

    return jsonify({'res': full_data.hex(), "name": name}), 200

@app.route('/decrypt/CBC', methods=['POST'])
def decrypt_cbc():
    data = request.json
    response, valid = validate_request_data(data, ['name', 'key', 'ciphertext'])
    if not valid:
        return jsonify(response), 400

    name = data['name']
    key = data['key'].encode()

    try:
        raw = bytes.fromhex(data['ciphertext'])
    except ValueError:
        return jsonify({"error": "Ciphertext is not a valid hexadecimal string."}), 400


    if not raw.startswith(b"MODE:CBC\n"):
        return jsonify({"error": "Wrong encryption mode. Expected CBC."}), 400

    ciphertext = raw[len(b"MODE:CBC\n"):]
    iv = b"JEODB34DOlgSHuRP"
    decrypted_plaintext = cbc_decrypt(ciphertext, key, iv)
    if decrypted_plaintext is None:
        return jsonify({"error": "Invalid ciphertext or corrupted data."}), 400
    try:
        decoded = decrypted_plaintext.decode()
    except UnicodeDecodeError:
        return jsonify({"error": "Decryption succeeded but output is not valid UTF-8."}), 400

    return jsonify({'res': decoded, "name": name}), 200

@app.route('/encrypt/CTR', methods=['POST'])
def encrypt_ctr():
    data = request.json
    response, valid = validate_request_data(data, ['name', 'key', 'plaintext'])
    if not valid:
        return jsonify(response), 400

    name = data['name']
    key = data['key'].encode()
    plaintext = data['plaintext'].encode()
    nonce = b"ABJ3k6lq12345678"  # 16 bajtów

    ciphertext = ctr_encrypt(plaintext, key, nonce)

    header = b"MODE:CTR\n"
    full_data = header + ciphertext

    return jsonify({'res': full_data.hex(), "name": name}), 200

@app.route('/decrypt/CTR', methods=['POST'])
def decrypt_ctr():
    data = request.json
    response, valid = validate_request_data(data, ['name', 'key', 'ciphertext'])
    if not valid:
        return jsonify(response), 400

    name = data['name']
    key = data['key'].encode()
    
    try:
        raw = bytes.fromhex(data['ciphertext'])
    except ValueError:
        return jsonify({"error": "Ciphertext is not a valid hexadecimal string."}), 400

    if not raw.startswith(b"MODE:CTR\n"):
        return jsonify({"error": "Wrong encryption mode. Expected CTR."}), 400

    ciphertext = raw[len(b"MODE:CTR\n"):]

    nonce = b"ABJ3k6lq12345678"  # dokładnie 16 bajtów
    decrypted_plaintext = ctr_decrypt(ciphertext, key, nonce)
    if decrypted_plaintext is None:
        return jsonify({"error": "Invalid ciphertext or corrupted data."}), 400
    try:
        decoded = decrypted_plaintext.decode()
    except UnicodeDecodeError:
        return jsonify({"error": "Decryption succeeded but output is not valid UTF-8."}), 400

    return jsonify({'res': decoded, "name": name}), 200

@app.route('/encrypt/ECB', methods=['POST'])
def encrypt_ecb():
    data = request.json
    response, valid = validate_request_data(data, ['name', 'key', 'plaintext'])
    if not valid:
        return jsonify(response), 400

    name = data['name']
    key = data['key'].encode()
    plaintext = data['plaintext'].encode()
    ciphertext = ecb_encrypt(plaintext, key)

    header = b"MODE:ECB\n"
    full_data = header + ciphertext

    return jsonify({'res': full_data.hex(), "name": name}), 200

@app.route('/decrypt/ECB', methods=['POST'])
def decrypt_ecb():
    data = request.json
    response, valid = validate_request_data(data, ['name', 'key', 'ciphertext'])
    if not valid:
        return jsonify(response), 400

    name = data['name']
    key = data['key'].encode()

    try:
        raw = bytes.fromhex(data['ciphertext'])
    except ValueError:
        return jsonify({"error": "Ciphertext is not a valid hexadecimal string."}), 400

    if not raw.startswith(b"MODE:ECB\n"):
        return jsonify({"error": "Wrong encryption mode. Expected ECB."}), 400

    #ciphertext = bytes.fromhex(data['ciphertext'])
    ciphertext = raw[len(b"MODE:ECB\n"):]

    decrypted_plaintext = ecb_decrypt(ciphertext, key)
    if decrypted_plaintext is None:
        return jsonify({"error": "Invalid ciphertext or corrupted data."}), 400
    try:
        decoded = decrypted_plaintext.decode()
    except UnicodeDecodeError:
        return jsonify({"error": "Decryption succeeded but output is not valid UTF-8."}), 400

    return jsonify({'res': decoded, "name": name}), 200

if __name__ == "__main__":
    app.run(debug=True)