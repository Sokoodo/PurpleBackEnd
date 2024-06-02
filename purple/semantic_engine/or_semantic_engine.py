import zope
from pm4py import PetriNet

from purple.semantic_engine.i_semantic_engine import ISemanticEngine


@zope.interface.implementer(ISemanticEngine)
class OrSemanticEngine:
    def __init__(self, model):
        self.__model: PetriNet = model
        self.__allPlaces: [str] = []
        self.__allTransitions: [str] = []
        self.__initialPlace: str = ""
        self.__finalPlace: str = ""
        self.initialize_components()

    def get_model(self):
        return self.__model

    def get_initial_state(self):
        return self.__initialPlace

    def initialize_components(self):
        for p in self.__model.places:
            if len(p.in_arcs) == 0:
                self.__initialPlace = p
            if len(p.out_arcs) == 0:
                self.__finalPlace = p

        for t in self.__model.transitions:
            self.__allTransitions.append(t.name)
        for p in self.__model.places:
            self.__allPlaces.append(p.name)
        # print(self.__initialPlace)
        # print(self.__finalPlace)
        pass

    def get_next_transitions(self, old_element: str):
        transitions = []
        for t in self.__model.transitions:
            for in_arc in t.in_arcs:
                if str(old_element) == str(in_arc.source):
                    transitions.append(t.name)

        if len(transitions) != 0:
            for t in transitions:
                print("trans=" + t)

        return transitions

    def get_next_places(self, old_element: str):
        places: [str] = []

        for p in self.__model.places:
            for in_arc in p.in_arcs:
                if old_element == in_arc.source.name:
                    places.append(p.name)

        strCom = ''
        if len(places) != 0:
            for p in places:
                strCom = strCom + p
        print("plc=" + strCom)

        return places
