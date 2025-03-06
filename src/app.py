from flask import Flask, request, abort
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from model import Entry

app = Flask(__name__)
app.json.sort_keys = False

engine = create_engine("sqlite:///db/dictionary.db")

# TODO: add index page

# dictionary query
@app.route("/dictionary")
def get_entries():
    with Session(engine) as sess:
        # filter for searching keys
        key = request.args.get("key", type=str, default="")

        # max number of entries in response
        size = request.args.get("size", type=int, default=32)
        size = 32 if size > 32 or size < 0 else size

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
@app.route("/dictionary/<int:id>")
def get_entry(id):
    with Session(engine) as sess:
        query = select(Entry).where(Entry.id == id)

        entry = sess.execute(query).scalars().first()

        if not entry:
            abort(400)

        return entry.to_dict()