class NumberTooBigError(Exception):
    def __init__(self, message="Number of cocktails in the database shouldn't be bigger than 2"):
        self.message = message
        super().__init__(self.message)