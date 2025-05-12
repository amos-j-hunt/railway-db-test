from flask import current_app as app, render_template, request, redirect, url_for
from sqlalchemy import or_
from collections import defaultdict
from .models import CollectionEntry, PrintingsCard, DeckName, DeckEntry
from . import db

@app.route("/")
def index():
    coll_q  = request.args.get("collection_search", "")
    print_q = request.args.get("printings_search", "")

    # Filter personal collection by name or text
    if coll_q:
        coll_entries = CollectionEntry.query.filter(
            or_(
                CollectionEntry.name.ilike(f"%{coll_q}%"),
                CollectionEntry.text.ilike(f"%{coll_q}%")
            )
        ).all()
    else:
        coll_entries = CollectionEntry.query.all()

    # Filter all printings by name or text
    if print_q:
        print_entries = PrintingsCard.query.filter(
            or_(
                PrintingsCard.name.ilike(f"%{print_q}%"),
                PrintingsCard.text.ilike(f"%{print_q}%")
            )
        ).limit(100).all()
    else:
        print_entries = PrintingsCard.query.limit(100).all()

    return render_template(
        "index.html",
        coll_entries=coll_entries,
        print_entries=print_entries,
        coll_q=coll_q,
        print_q=print_q
    )

@app.route("/add_printing", methods=["POST"])
def add_printing():
    uuid = request.form["uuid"]
    card = PrintingsCard.query.filter_by(uuid=uuid).first_or_404()

    entry = CollectionEntry.query.filter_by(uuid=uuid).first()
    if entry:
        entry.quantity += 1
    else:
        # Build a dict of all columns except the PK 'id'
        data = {
            c.name: getattr(card, c.name)
            for c in PrintingsCard.__table__.columns
            if c.name != "id"
        }
        data["quantity"] = 1

        # Unpack into your CollectionEntry
        entry = CollectionEntry(**data)
        db.session.add(entry)

    db.session.commit()
    return redirect(url_for("index"))


@app.route("/decrement_card", methods=["POST"])
def decrement_card():
    uuid = request.form["uuid"]
    entry = CollectionEntry.query.filter_by(uuid=uuid).first_or_404()
    entry.quantity -= 1
    if entry.quantity <= 0:
        db.session.delete(entry)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/deck", methods=["GET","POST"])
def deck_builder():
    # Handle New Deck creation
    if request.method == "POST" and request.form.get("action") == "new_deck":
        next_idx = DeckName.query.count() + 1
        deck = DeckName(name=f"Deck {next_idx}")
        db.session.add(deck)
        db.session.commit()
        return redirect(url_for("deck_builder", deck_id=deck.id))

    # Determine which deck to show
    deck_id = request.args.get("deck_id", type=int)
    if deck_id:
        deck = DeckName.query.get_or_404(deck_id)
    else:
        deck = DeckName.query.order_by(DeckName.id.desc()).first()
        if not deck:
            deck = DeckName(name="Deck 1")
            db.session.add(deck)
            db.session.commit()

    # Handle Rename
    if request.method == "POST" and request.form.get("action") == "rename_deck":
        new_name = request.form["deck_name"].strip()
        if new_name:
            deck.name = new_name
            db.session.commit()
        return redirect(url_for("deck_builder", deck_id=deck.id))

    # Search collection on deck page
    coll_search = request.args.get("coll_search", "")
    if coll_search:
        coll_entries = CollectionEntry.query.filter(
            or_(
                CollectionEntry.name.ilike(f"%{coll_search}%"),
                CollectionEntry.text.ilike(f"%{coll_search}%")
            )
        ).all()
    else:
        coll_entries = CollectionEntry.query.all()

    # Deck entries
    deck_entries = DeckEntry.query.filter_by(deck_id=deck.id).all()
    deck_display = []
    for de in deck_entries:
        card = PrintingsCard.query.filter_by(uuid=de.uuid).first()
        deck_display.append((de, card))

    # Group by manaValue
    by_cost = defaultdict(list)
    for de, card in deck_display:
        cost = card.manaValue or 0
        by_cost[cost].append((de, card))

    # All saved decks for the dropdown
    all_decks = DeckName.query.order_by(DeckName.id).all()

    return render_template(
        "deck.html",
        all_decks=all_decks,
        deck=deck,
        coll_entries=coll_entries,
        by_cost=sorted(by_cost.items()),
        coll_search=coll_search
    )

@app.route("/deck/add", methods=["POST"])
def deck_add():
    deck_id = int(request.form["deck_id"])
    uuid    = request.form["uuid"]
    de = DeckEntry.query.filter_by(deck_id=deck_id, uuid=uuid).first()
    if de:
        de.quantity += 1
    else:
        de = DeckEntry(deck_id=deck_id, uuid=uuid, quantity=1)
        db.session.add(de)
    db.session.commit()
    return redirect(url_for("deck_builder", deck_id=deck_id))

@app.route("/deck/remove", methods=["POST"])
def deck_remove():
    deck_id = int(request.form["deck_id"])
    uuid    = request.form["uuid"]
    de = DeckEntry.query.filter_by(deck_id=deck_id, uuid=uuid).first_or_404()
    de.quantity -= 1
    if de.quantity <= 0:
        db.session.delete(de)
    db.session.commit()
    return redirect(url_for("deck_builder", deck_id=deck_id))
