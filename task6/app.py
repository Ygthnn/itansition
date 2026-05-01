from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    host="localhost",
    database="fake_users",
    user="postgres",
    password="1234"
)

@app.route("/", methods=["GET", "POST"])
def index():
    users = []
    if request.method == "POST":
        locale = request.form.get("locale", "en_US")
        seed = int(request.form.get("seed", 123))
        batch = int(request.form.get("batch", 0))
        batch_size = int(request.form.get("batch_size", 10))

        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM generate_fake_users(%s, %s, %s, %s)",
            (locale, seed, batch, batch_size)
        )
        users = cur.fetchall()
        cur.close()

    return render_template("index.html", users=users)

if __name__ == "__main__":
    app.run(debug=True)