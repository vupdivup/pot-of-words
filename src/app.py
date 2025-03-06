from flask import Flask, request, abort, render_template
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from model import Entry

app = Flask(__name__)
app.json.sort_keys = False

engine = create_engine("sqlite:///db/dictionary.db")

@app.route("/")
def get_index():
    return render_template("index.html")

@app.errorhandler(404)
def get_404(e):
    return render_template(
        "error.html",
        heading="404 Not Found",
        message="There is nothing here."
    )

@app.errorhandler(400)
def get_400(e):
    return render_template(
        "error.html",
        heading="400 Bad Request",
        message="An invalid request was sent to the server."
    )

# dictionary query
@app.route("/entries")
def get_entries():
    with Session(engine) as sess:
        # filter for searching keys
        key = request.args.get("key", type=str, default="")

        # max number of entries in response
        size = request.args.get("size", type=int, default=32)
        size = 32 if size > 128 or size < 0 else size

        # query offset, useful for pagination
        offset = request.args.get("offset", type=int, default=0)
        offset = 0 if offset < 0 else offset

        query = select(Entry)

        # NOTE: this should be safe, it compiles to bound param expression
        query = query.where(Entry.key.like("{}%".format(key)))
        
        query = query.order_by(Entry.id).limit(size).offset(offset)

        entries = sess.execute(query).scalars()

        return [e.to_dict() for e in entries]

# endpoint for single dictionary entry
@app.route("/entries/<int:id>")
def get_entry(id):
    with Session(engine) as sess:
        query = select(Entry).where(Entry.id == id)

        entry = sess.execute(query).scalars().first()

        if not entry:
            abort(400)

        return entry.to_dict()