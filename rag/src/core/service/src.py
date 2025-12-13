from abc import ABC, abstractmethod

class GenerateService(ABC):
    @abstractmethod
    def generate(self, query: str) -> str:
        pass