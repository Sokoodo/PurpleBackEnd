import random

import zope
from pm4py import PetriNet

from purple.semantic_engine.i_semantic_engine import ISemanticEngine


@zope.interface.implementer(ISemanticEngine)
class OrSemanticEngine:
    def __init__(self, model):
        self.__model: PetriNet = model
        self.__allPlaces: [PetriNet.Place] = []
        self.__allTransitions: [PetriNet.Transition] = []
        self.__initialPlace: PetriNet.Place = NotImplemented
        self.__finalPlace: PetriNet.Place = NotImplemented
        self.initialize_components()

    def get_model(self):
        return self.__model

    def get_initial_state(self):
        if self.__initialPlace != NotImplemented:
            return self.__initialPlace

    def initialize_components(self):
        for p in self.__model.places:
            if len(p.in_arcs) == 0:
                self.__initialPlace = p
            if len(p.out_arcs) == 0:
                self.__finalPlace = p

        for t in self.__model.transitions:
            self.__allTransitions.append(t)
        for p in self.__model.places:
            self.__allPlaces.append(p)
        # print(self.__initialPlace)
        # print(self.__finalPlace)
        pass

    def get_next_transition(self, old_element: PetriNet.Place):
        transitions: [PetriNet.Transition] = []

        if old_element is not None and len(old_element.out_arcs) > 0:
            for t in self.__model.transitions:
                for out_arc in old_element.out_arcs:
                    if str(t.name) == str(out_arc.target.name):
                        transitions.append(t)

        return transitions[random.randint(0, len(transitions)-1)] if len(transitions) > 0 else None

    def get_next_places(self, old_element: PetriNet.Transition):
        places: [PetriNet.Place] = []

        for p in self.__model.places:
            for in_arc in p.in_arcs:
                if str(old_element.name) == str(in_arc.source.name):
                    places.append(p)

        return places

    def get_next_step(self, prefix: PetriNet.Place):
        pass
