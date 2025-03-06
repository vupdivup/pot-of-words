from flask import Flask, request, abort
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from model import Entry

app = Flask(__name__)
app.json.sort_keys = False

engine = create_engine("sqlite:///db/dictionary.db")

@app.route("/dictionary")
def get_entries():
    with Session(engine) as sess:
        # provide filters for key
        key = request.args.get("key", type=str)
        size = request.args.get("size", type=int, default=32)
        offset = request.args.get("offset", type=int, default=0)

        query = select(Entry)

        if not key is None:
            # NOTE: this is unsafe!!
            query = query.where(Entry.key.like("{}%".format(key)))
        
        query = query.order_by(Entry.id).limit(size).offset(offset)

        entries = sess.execute(query).scalars()

        return [e.to_dict() for e in entries]

@app.route("/dictionary/<int:id>")
def get_entry(id):
    with Session(engine) as sess:
        query = select(Entry).where(Entry.id == id)

        entry = sess.execute(query).scalars().first()

        if not entry:
            abort(400)

        return entry.to_dict()