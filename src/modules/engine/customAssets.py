class CustomAsset(object):

    def __init__(self, code: str, issuer: str, amount: float,image: str,homepage: str):
        self.code = code
        self.issuer = issuer
        self.amount = amount
        self.image = image
        self.homepage = homepage
    
    def __str__(self):
        return f"{self.code} - {self.issuer} - {self.amount} - {self.image} - {self.homepage}"