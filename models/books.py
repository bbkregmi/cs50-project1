class Book:
    def __init__(self, id, isbn, title, author, year, avg_review=None, review_count=None):
        self.id = id
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.avg_review = avg_review
        self.review_count = review_count
    
    def __hash__(self):
        return hash((
            self.id, self.isbn, 
            self.title, self.author, self.year,
            self.avg_review, self.review_count))
    
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id