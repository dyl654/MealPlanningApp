class Ingredient:
    def __init__(self, name: str, quantity: str = None, optional: bool = False):
        self.name = name
        self.quantity = quantity
        self.optional = optional

    def __repr__(self):
        return f"Ingredient(name={self.name}, quantity={self.quantity}, optional={self.optional})"


class Recipe:
    def __init__(self, title: str):
        self.title = title
        self.Ingredients: list[Ingredient] = []
        self.Instructions: list[str] = []

    def __repr__(self):
        return f"Recipe(title={self.title}, Ingredients={self.Ingredients}, Instructions={self.Instructions})"

