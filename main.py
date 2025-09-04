from flask import Flask, render_template, request
import pyshorteners

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    print("Página home llamada")
    new_url = None
    if request.method == "POST":
        original_url = request.form["url"]
        print(f"URL recibida: {original_url}")
        shortener = pyshorteners.Shortener()
        new_url = shortener.tinyurl.short(original_url)
    return render_template("form.html", new_url=new_url)

@app.route("/test")
def test():
    print("Ruta /test llamada")
    return "Funciona!"

if __name__ == "__main__":
    app.run(debug=True)
