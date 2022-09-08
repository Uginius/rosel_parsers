class Product:
    def __init__(self):
        self.shop_id = None
        self.rosel_id = None
        self.name = None
        self.url = None
        self.trade_mark = None
        self.status = None
        self.price = None
        self.order = None
        self.rating = None
        self.feedbacks = None

    def out_items(self):
        return self.shop_id, self.name, self.url, self.status, self.price, self.rating, self.feedbacks

    def json_items(self):
        return {
            self.shop_id: {
                'rosel_id': self.rosel_id,
                'brand': self.trade_mark,
                'name': self.name,
                'url': self.url,
                'status': self.status,
                'price': self.price,
                'rating': self.rating,
                'feedbacks': self.feedbacks,
            }
        }
