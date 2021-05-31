from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel

class PIDControl:
    def __init__(self, p, d):
        self.p = p
        self.d = d

    def update(self, car: CartesianDynamicBicycleModel):
        return -self.p*car.z[car.StateIdx.Y] - self.d*car.ydot
