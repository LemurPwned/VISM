from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def create(self, size):
        pass

    @abstractmethod
    def rotate(self, *angles):
        """
        rotates object by specifed angles
        """
        pass

    @abstractmethod
    def translate(self, *vector):
        """
        translates object by a vector specified in the argument
        """
        pass

    @abstractmethod
    def move(self, *position):
        """
        moves object from current position to new position passed in
        this method
        """
        pass
