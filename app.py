from flask import Flask, jsonify, request
from datetime import datetime, timedelta, timezone
import jwt

# Replace with your secret key (keep it secure!)
SECRET_KEY = 'your_secret_key'  # Replace with a strong, random string

app = Flask(__name__)

# Sample credit score data (replace with your actual data source logic)
credit_scores = {
    "JohnDoe": 720,
    "JaneSmith": 800
}

class InvalidTokenError(Exception):
    pass

def generate_token(user_id):
    """Generates a JWT access token."""
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(minutes=5),  # Use timezone.utc here
        'iat': datetime.now(timezone.utc),  # Use timezone.utc here
        'user_id': user_id
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verifies the JWT access token and raises exceptions for errors."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")


@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/login', methods=['POST'])
def login():
    """Handles login requests and generates access token."""
    # Replace with your authentication logic (e.g., username/password)
    if request.json and 'username' in request.json:
        username = request.json['username']
        # Simulate authentication (replace with actual validation)
        if username == 'admin':
            return jsonify({'token': generate_token(username)})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401  # Unauthorized
    else:
        return jsonify({'error': 'Missing username'}), 400  # Bad request

@app.route('/credit-scores/<name>', methods=['GET'])
def get_credit_score(name):
    """Retrieves credit score for authorized users."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Missing authorization token'}), 401

    token = auth_header.split()[1] if auth_header else None
    try:
        user_id = verify_token(token)
    except InvalidTokenError as e:
        return jsonify({'error': str(e)}), 401

    if name in credit_scores:
        score = credit_scores[name]
        return jsonify({'name': name, 'credit_score': score}), 200
    else:
        return jsonify({'error': 'Credit score not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False for production