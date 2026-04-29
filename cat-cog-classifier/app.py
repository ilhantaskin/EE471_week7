import os
import subprocess
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    print("REQUEST METHOD:", request.method)
    result = None
    error = None
    uploaded_file = None

    if request.method == "POST":
        print("POST RECEIVED")
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
        uploaded_file = filename

        try:
            completed = subprocess.run(
                ["cog", "predict", "-i", f"image=@uploads/{filename}"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=True
            )
            result = completed.stdout.strip()
        except subprocess.CalledProcessError as e:
            error = e.stderr or e.stdout or str(e)

    return render_template(
        "index.html",
        result=result,
        error=error,
        uploaded_file=uploaded_file
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)