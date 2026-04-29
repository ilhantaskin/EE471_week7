import os
import subprocess
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        if "image" not in request.files:
            error = "Please upload an image."
            return render_template("index.html", error=error)

        file = request.files["image"]
        if file.filename == "":
            error = "No file selected."
            return render_template("index.html", error=error)

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            completed = subprocess.run(
                ["cog", "predict", "-i", f"image=@{filepath}"],
                capture_output=True,
                text=True,
                check=True
            )
            result = completed.stdout
        except subprocess.CalledProcessError as e:
            error = e.stderr or e.stdout or str(e)

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)