import json
from config import DB_PATH
from flask import Flask, request, abort
from sqlalchemy import create_engine, text

app = Flask(__name__)

engine = create_engine(DB_PATH)

@app.route("/dictionary")
def get_keys():
    # TODO: order object keys

    with engine.connect() as con:
        # return a list of definitions related to an entry
        def get_defs(entry_id):
            query = text(
                "SELECT definition FROM definition WHERE entry_id = :entry_id"
            )

            defs = con.execute(query, {"entry_id": entry_id}).all()

            return [d._asdict()["definition"] for d in defs]

        # get URL params
        id = request.args.get("id", type=int)
        key = request.args.get("key", type=str)

        # ======================================================================
        # 1. QUERY BY ENTRY ID
        # ======================================================================

        if id:
            entry_query = text(f"SELECT * FROM entry WHERE id = :id")

            entry = con.execute(entry_query, {"id": id}).first()

            # 404 if entry with supplied ID doesn't exist
            if not entry:
                abort(404)
            
            entry = entry._asdict()

            entry["definitions"] = get_defs(entry["id"])

            return entry
        
        # ======================================================================
        # 2. QUERY BY KEY
        # ======================================================================

        if key:
            entry_query = text("SELECT * FROM entry WHERE key = :key")

            entry = con.execute(entry_query, {"key": key}).first()

            if not entry:
                abort(404)

            entry = entry._asdict()

            entry["definitions"] = get_defs(entry["id"])

            return entry

        # ======================================================================
        # 3. QUERY ALL ENTRIES
        # ======================================================================

        # TODO: paginate
        # TODO: order by ID
        
        query = text("SELECT key, id FROM entry")

        rows = con.execute(query).all()

        entries = [r._asdict() for r in rows]

        # include URL which gets definitions for an entry
        for x in entries:
            x["url"] = f"{request.host_url}dictionary?id={x["id"]}"

        return entries