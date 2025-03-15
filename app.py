from flask import Flask, render_template, request, redirect, url_for
import os
from imagechain import ImageChain

app = Flask(__name__)
imagechain = ImageChain()

@app.route("/")
def home():
    """Render the home page with the imagechain."""
    return render_template("index.html", chain=imagechain.chain)

@app.route("/upload", methods=["POST"])
def upload():
    """Handle image upload and add it to the imagechain."""
    if "file" not in request.files:
        return redirect(url_for("home"))
    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("home"))
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)
    imagechain.add_block(file_path)
    return redirect(url_for("home"))


if __name__ == "__main__":
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
    