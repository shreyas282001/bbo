import email
import bcrypt
from flask import Flask, render_template, request, jsonify, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, session


app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = b'\x9f\x15\x1c\xf4\x1a\xf3\xb8\xd2V\xd3\xe7\xd3\x95\x88\x03\xcb\x9a9\x11\x96@\xb4\xc1'


# Firebase setup
cred = credentials.Certificate(r"F:\BBO\webportal\bbo\bbo24-88654-firebase-adminsdk-8fbjo-86539d93e7.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

#login and reg

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match", 400

        # Hash the password for security
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Check if the email is already registered
        users_ref = db.collection('users').where('email', '==', email).stream()
        if any(users_ref):
            return "Email is already registered", 400

        # Save user data to Firebase
        db.collection('users').add({
            'email': email,
            'password': hashed_password
        })
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists in Firebase
        users_ref = db.collection('users').where('email', '==', email).stream()
        user_doc = next(users_ref, None)

        if user_doc:
            user = user_doc.to_dict()
            stored_password = user.get('password')

            # Validate the password
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                session['user_email'] = email  # Store user in session
                return redirect(url_for('index'))  # Navigate to index
            else:
                return "Invalid credentials", 401
        else:
            return "User not found", 404

    return render_template('login.html')


@app.route("/index")
def index():
    # Fetch all requests from Firestore
    users_ref = db.collection('organisations')
    docs = users_ref.stream()
    data = [{"id": doc.id, **doc.to_dict()} for doc in docs]
    return render_template("index.html", requests=data)

@app.route("/details/<string:request_id>")
def details(request_id):
    # Fetch specific request details
    doc_ref = db.collection('organisations').document(request_id)
    doc = doc_ref.get()
    if doc.exists:
        return render_template("details.html", data=doc.to_dict(), request_id=request_id)
    else:
        return "Request not found", 404

@app.route("/accept/<string:request_id>", methods=["POST"])
def accept_request(request_id):
    try:
        doc_ref = db.collection('organisations').document(request_id)
        doc = doc_ref.get()
        if doc.exists:
            # Move data to 'finalorg' collection
            db.collection('finalorg').document(request_id).set(doc.to_dict())
            # Delete original document
            doc_ref.delete()
            return jsonify({"message": "Request accepted!"}), 200
        else:
            return jsonify({"error": "Request not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reject/<string:request_id>", methods=["POST"])
def reject_request(request_id):
    try:
        doc_ref = db.collection('organisations').document(request_id)
        doc_ref.delete()
        return jsonify({"message": "Request rejected!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/users')
def users():
    try:
        # Fetch data from Firebase Firestore
        users_ref = db.collection('users')  # Collection name
        docs = users_ref.stream()  # Fetch all documents from the 'users' collection
        
        # Transform Firestore docs into a list of dictionaries
        users_data = []
        for doc in docs:
            data = doc.to_dict()  # Convert document to dictionary
            data['id'] = doc.id     # Add document id to data (optional)
            users_data.append(data)

        return render_template('users.html', users_data=users_data)
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/approved-businesses')
def approved_businesses():
    # Fetch data from Firebase Firestore
    finalorg_ref = db.collection('finalorg')
    docs = finalorg_ref.stream()
    
    # Retrieve data and print it for debugging
    finalorg_data = [{doc.id: doc.to_dict()} for doc in docs]
    print("Fetched Data: ", finalorg_data)  # Debugging output
    
    return render_template('approved_businesses.html', finalorg_data=finalorg_data)
    
    
@app.route('/user-details/<user_id>')
def user_details(user_id):
    # Fetch user details from Firebase Firestore
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    
    if user.exists:
        return render_template('user_details.html', user=user.to_dict())
    else:
        return "User not found", 404
    
@app.route('/delete-user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        # Fetch the user data from Firestore and delete by ID
        users_ref = db.collection('users')
        users_ref.document(user_id).delete()

        return jsonify({"success": True, "message": "User deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route('/send-email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        recipient_email = request.form['recipient_email']
        subject = request.form['subject']
        message = request.form['message']

        try:
            # Replace with your actual email address (sender)
            sender_email = 'bhavsarbusinessorganization@gmail.com'

            # Configure SMTP server details (replace with your provider's settings)
            smtp_server = 'bhavsarbusinessorganization@gmail.com'
            smtp_port = 587

            # Create email message
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg.set_content(message)

            # Create secure SSL connection
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                # Replace with your email credentials (username and password)
                server.login(bhavsarbusinessorganization@email.com, 'Bhavsarbusiness@24') # type: ignore
                server.send_message(msg)

            return jsonify({'message': 'Email sent successfully!'}), 200
        except Exception as e:
            return jsonify({'error': f'Error sending email: {str(e)}'}), 500

@app.route('/logout')
def logout():
    session.clear()  # Clear the session to log out the user
    return redirect(url_for('login'))

@app.route('/delete-business/<key>', methods=['DELETE'])
def delete_business(key):
    try:
        # Access the 'finalorg' collection in Firestore
        doc_ref = db.collection('finalorg').document(key)
        
        # Check if the document exists
        doc = doc_ref.get()
        if not doc.exists:
            return jsonify({"error": "Business not found"}), 404
        
        # Delete the document
        doc_ref.delete()
        return jsonify({"success": True, "message": "Business deleted successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500




if __name__ == "__main__":
    app.run(debug=True)
