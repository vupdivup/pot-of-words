from flask import Flask, request, abort
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from model import Entry

app = Flask(__name__)
app.json.sort_keys = False

engine = create_engine("sqlite:///db/dictionary.db")

@app.route("/dictionary")
def get_keys():
    with Session(engine) as sess:
        # get URL params
        id = request.args.get("id", type=int)
        key = request.args.get("key", type=str)

        # ======================================================================
        # 1. QUERY BY ENTRY ID
        # ======================================================================

        # TODO: id = 0 throws error
        # TODO: test injection

        if id:
            query = select(Entry).where(Entry.id == id)

            entry = sess.execute(query).scalars().first()

            if not entry:
                abort(404)

            return entry.to_dict()
        
        # ======================================================================
        # 2. QUERY BY KEY
        # ======================================================================

        if key:
            query = select(Entry).where(Entry.key == key)

            entry = sess.execute(query).scalars().first()

            if not entry:
                abort(404)

            return entry.to_dict()
        
        query = sess.execute(select(Entry))

        return 