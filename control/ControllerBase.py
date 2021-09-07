from abc import ABC, abstractmethod
from paths.PathBase import PathBase
from dynamics import CartesianDynamicBicycleModel


class ControllerBase(ABC):

    @abstractmethod
    def update(self, car: CartesianDynamicBicycleModel, path: PathBase) -> float:
        ...
