from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import boto3
from botocore.exceptions import ClientError
import logging

app = Flask(__name__)
CORS(app)

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

@app.route('/submit_form', methods=['POST'])
def submit_form():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        return jsonify({'error': 'All fields are required!'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return jsonify({'error': str(err)}), 500

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
                    }
                }
            }
        )
    except ClientError as e:
        logging.error(f"SES error: {e}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'success': 'Message sent successfully!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)






# import os
# from flask import Flask, request, jsonify
# from flask_mail import Mail, Message
# from flask_cors import CORS
# import mysql.connector

# app = Flask(__name__)
# CORS(app)

# # Configurations for Flask-Mail
# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
# app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
# app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'

# mail = Mail(app)

# # Database connection
# db_config = {
#     'user': os.getenv('DB_USER'),
#     'password': os.getenv('DB_PASSWORD'),
#     'host': os.getenv('DB_HOST'),
#     'database': os.getenv('DB_NAME')
# }

# @app.route('/submit_form', methods=['POST'])
# def submit_form():
#     data = request.get_json()
#     name = data.get('name')
#     email = data.get('email')
#     message = data.get('message')

#     # Validate input
#     if not name or not email or not message:
#         return jsonify({'error': 'Missing data'}), 400

#     # Save to database
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO contact_form (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
#     conn.commit()
#     cursor.close()
#     conn.close()

#     # Send email
#     msg = Message('Contact Form Submission',
#                   sender=os.getenv('MAIL_USERNAME'),
#                   recipients=['recipient@example.com'])
#     msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
#     mail.send(msg)

#     return jsonify({'message': 'Form submitted successfully'}), 200

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

