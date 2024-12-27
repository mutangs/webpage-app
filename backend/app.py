from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import boto3
from botocore.exceptions import ClientError
import logging
from email_validator import validate_email, EmailNotValidError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
CORS(app)

# Set up rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per minute"]
)

# Configure Amazon SES
app.config['SES_REGION'] = os.environ.get('SES_REGION')
app.config['SES_SENDER'] = os.environ.get('SES_SENDER')
app.config['SES_RECIPIENT'] = os.environ.get('SES_RECIPIENT')

ses_client = boto3.client('ses', region_name=app.config['SES_REGION'])

# Configure MySQL connection
db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME')
}

# Set up logging
logging.basicConfig(level=logging.INFO)

def validate_email_address(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

@app.route('/submit_form', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit for form submissions
def submit_form():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        return jsonify({'error': 'All fields are required!'}), 400
        
    if not validate_email_address(email):
        return jsonify({'error': 'Invalid email address!'}), 400

    if len(message) < 10:
        return jsonify({'error': 'Message must be at least 10 characters long!'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
        conn.commit()
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    # Send confirmation email
    try:
        response = ses_client.send_email(
            Source=app.config['SES_SENDER'],
            Destination={
                'ToAddresses': [app.config['SES_RECIPIENT']],
            },
            Message={
                'Subject': {
                    'Data': 'New Message from Contact Form',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': f"Name: {name}\nEmail: {email}\nMessage: {message}",
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': f"""
                            <h2>New Contact Form Submission</h2>
                            <p><strong>Name:</strong> {name}</p>
                            <p><strong>Email:</strong> {email}</p>
                            <p><strong>Message:</strong><br>{message}</p>
                        """,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        logging.info(f"Email sent successfully! Message ID: {response['MessageId']}")
    except ClientError as e:
        logging.error(f"SES error: {e}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'success': 'Message sent successfully!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Set debug=False in production
