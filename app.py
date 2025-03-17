from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import uuid
from imagechain import ImageChain

app = Flask(__name__)
imagechain = ImageChain()

@app.route("/")
def home():
    """Render the home page with the imagechain."""
    # Reload the blockchain from MongoDB
    imagechain.chain = imagechain.load_from_mongodb()
    
    # Verify the blockchain integrity
    is_valid = imagechain.verify_chain_real_time()
    
    return render_template("index.html", chain=imagechain.chain, is_valid=is_valid)

@app.route("/upload", methods=["POST"])
def upload():
    """Handle image upload and add it to the imagechain."""
    if "file" not in request.files:
        return redirect(url_for("home"))
    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("home"))
    
    # Save the uploaded file temporarily
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)
    
    # Add the image to the blockchain
    imagechain.add_block(file_path)
    
    # Clean up the temporary file
    os.remove(file_path)
    
    return redirect(url_for("home"))

@app.route("/image/<file_id>")
def get_image(file_id):
    """Serve an image from MongoDB using its file_id."""
    # Generate a unique filename for the temporary image
    temp_image_path = f"temp_image_{uuid.uuid4().hex}.png"
    try:
        # Retrieve the image from MongoDB
        imagechain.get_image_from_mongodb(file_id, temp_image_path)
        
        # Serve the image
        return send_file(temp_image_path, mimetype="image/png")
    except Exception as e:
        return str(e), 404
    finally:
        # Clean up the temporary file after it has been served
        if os.path.exists(temp_image_path):
            try:
                os.remove(temp_image_path)
            except PermissionError:
                # If the file is still in use, skip deletion (it will be cleaned up later)
                pass

if __name__ == "__main__":
    app.run(debug=True)