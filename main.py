from interface import Interface
from callbacks import Callbacks

"""
    La clase app es responsable de la ejecución del programa en su conjunto, y es el punto de partida.
"""


class App:
    def __init__(self) -> None:
        self.interface = Interface(Callbacks())
        pass


if __name__ == "__main__":
    app = App()
