
class Individual:

    def __init__(self, number_of_panels: int):
        self.number_of_panels = number_of_panels
        self.fitness = 0.0

    def __repr__(self):
        return (
            f"Individual("
            f"panels={self.number_of_panels}, "
            f"fitness={self.fitness:.2f})"
        )
