
class Textbook:

    def __init__(self, title, price, source, siteSource):
        self._source = source
        self._title = title
        self._price = price
        self._siteSource = siteSource
        self._priceValue = float(self._price[1:])

    def getTitle(self):
        return self._title

    def getPrice(self):
        return self_.price

    def __lt__(self, rhsValue):
        return self._priceValue < rhsValue._priceValue

    def __repr__(self):
        
        return "Listing: " + self._title + "\nPrice: " + self._price + "\nfrom: " + self._siteSource
        
