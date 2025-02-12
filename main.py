from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, SessionLocal
from auth import verify_token
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Mount the templates directory
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
templates = Jinja2Templates(directory="templates")

# Sample Books
SAMPLE_BOOKS = [
    {"title": "Python 101", "author": "John Doe", "year": 2021},
    {"title": "Machine Learning Basics", "author": "Jane Smith", "year": 2020}
]

# Insert sample books at startup
@app.on_event("startup")
def startup():
    db = SessionLocal()
    for book in SAMPLE_BOOKS:
        existing_book = db.query(models.Book).filter(models.Book.title == book["title"]).first()
        if not existing_book:
            db.add(models.Book(**book))
    db.commit()
    db.close()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Updated root endpoint
@app.get("/")
def read_books(request: Request, db: Session = Depends(get_db)):
    books = crud.get_books(db)  # Fetch books
    print("Books fetched from DB:", books)  # Debugging line
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

# CRUD Endpoints
@app.get("/books/", response_model=list[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):
    return crud.get_books(db)

@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books/", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, book)

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.delete_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

# Secure Endpoint
@app.get("/secure/books", dependencies=[Depends(verify_token)])
def secure_books():
    return {"message": "This is a secure route"}
