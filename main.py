from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books-collection.db"

db = SQLAlchemy(model_class=Base)

class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


    def __repr__(self):
        return f'<Book {self.title}>'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    with app.app_context():
        result = db.session.execute(db.select(Book).order_by(Book.title))
        all_books = result.scalars().all()
    return  render_template("index.html",books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        with app.app_context():
            new_book = Book(title=request.form["title"], author=request.form["author"], rating=request.form["rating"])
            db.session.add(new_book)
            db.session.commit()

        return redirect(url_for('home'))
    return render_template("add.html")

@app.route("/delete")
def delete():
    book_title = request.args.get("book_title")

    book_to_delete = db.session.execute(db.select(Book).where(Book.title == book_title)).scalar()

    if book_to_delete:
        db.session.delete(book_to_delete)
        db.session.commit()

    return redirect(url_for("home"))

@app.route("/edit_page")
def edit_page():
    book_id = request.args.get("book_id", type=int)

    book = db.get_or_404(Book, book_id)

    return render_template("edit_webpage.html", book=book)

@app.route("/edit", methods=["GET", "POST"])
def edit_rating():
    book_id = request.args.get("book_id", type=int)

    book = db.get_or_404(Book, book_id)

    if request.method == "POST":
        book.rating = float(request.form["rating"])
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit_webpage.html", book=book)

if __name__ == "__main__":
    app.run(debug=True)

