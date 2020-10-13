class Book:

    def __init__(self, title, authors, info, cover, isbn='NA', rating='NA'):
        self.isbn = isbn
        self.title = title
        self.authors = authors
        self.rating = rating
        self.info = info
        self.cover = cover

    def __repr__(self):
        return f"Book: {self.title}, authors:{self.authors}"

    