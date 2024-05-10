from typing import Set

import zope.interface
from pm4py import PetriNet


class ISemanticEngine(zope.interface.Interface):
    def get_model(self):
        pass

    def get_initial_state(self):
        pass

    def find_initial_and_final_state(self):
        pass

    def get_next_step(self, old_place):
        pass


@zope.interface.implementer(ISemanticEngine)
class SemanticEngine:
    def __init__(self, model):
        self.__model: PetriNet = model
        self.__sources: Set[str] = set()
        self.__targets: Set[str] = set()
        self.__initialPlace: str = ""
        self.__finalPlace: str = ""
        self.find_initial_and_final_state()

    def get_model(self):
        return self.__model

    def get_initial_state(self):
        return self.__initialPlace

    def find_initial_and_final_state(self):
        for p in self.__model.places:
            if len(p.in_arcs) == 0:
                self.__initialPlace = p
            if len(p.out_arcs) == 0:
                self.__finalPlace = p

        # print(self.__initialPlace)
        # print(self.__finalPlace)

        for arc in self.__model.arcs:
            self.__sources.add(f"{arc.source.name}" or None)
            self.__targets.add(arc.target.name or None)

        # print("finito")
        pass

    def get_next_step(self, old_place):
        print(old_place)
        pass
