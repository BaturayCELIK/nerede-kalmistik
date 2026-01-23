from abc import ABC, abstractmethod


class BaseLLMClient(ABC):

    @abstractmethod
    def generate_recap(self, prompt: str) -> str:
        """
        Takes a recap prompt and returns a generated recap text.
        """
        pass
