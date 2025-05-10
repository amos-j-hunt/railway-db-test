from flask import current_app as app, render_template, request, redirect, url_for
from .models import CollectionEntry, PrintingsCard
from . import db


@app.route("/")
def index():
    # pull search terms from query string
    coll_q = request.args.get("collection_search", "")
    print_q = request.args.get("printings_search", "")

    # filter your personal collection
    if coll_q:
        coll_entries = CollectionEntry.query.filter(
            CollectionEntry.name.ilike(f"%{coll_q}%")
        ).all()
    else:
        coll_entries = CollectionEntry.query.all()

    # filter the printings (limit to first 100 for performance)
    if print_q:
        print_entries = PrintingsCard.query.filter(
            PrintingsCard.name.ilike(f"%{print_q}%")
        ).limit(100).all()
    else:
        print_entries = PrintingsCard.query.limit(100).all()

    return render_template(
        "index.html",
        coll_entries=coll_entries,
        print_entries=print_entries,
        coll_q=coll_q,
        print_q=print_q,
    )

@app.route("/add_printing", methods=["POST"])
def add_printing():
    uuid = request.form["uuid"]
    card = PrintingsCard.query.filter_by(uuid=uuid).first_or_404()

    entry = CollectionEntry.query.filter_by(uuid=uuid).first()
    if entry:
        entry.quantity += 1
    else:
        entry = CollectionEntry(
            uuid=card.uuid,
            name=card.name,
            setCode=card.setCode,          # ← was set_name
            type=card.type,                # ← was card_type
            colors=card.colors,            # adjust as needed
            rarity=card.rarity,
            manaCost=card.manaCost,
            quantity=1
        )
        db.session.add(entry)

    db.session.commit()
    return redirect(url_for("index"))
