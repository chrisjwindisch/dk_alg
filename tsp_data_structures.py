class GeoCity:
    def __init__(self, id, x, y):
        self.id = int(id)
        self.x = float(x)
        self.y = float(y)
        self.city = City(id=id)


class City:
    def __init__(self, id):
        self.id = int(id)


class OEdge:
    def __init__(self, city_a, city_b, cost):
        self.city_a = city_a
        self.city_b = city_b
        self.cost = int(cost)


class UEdge:
    def __init__(self, city_a, city_b, cost):
        self.city_a = city_a
        self.city_b = city_b
        self.cost = int(cost)
