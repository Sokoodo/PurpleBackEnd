import random

import zope
from pm4py import PetriNet
from pm4py.objects.bpmn.obj import Marking

from purple.semantic_engine.i_semantic_engine import ISemanticEngine


@zope.interface.implementer(ISemanticEngine)
class PetriSemanticEngine:
    def __init__(self, model):
        self.__model: PetriNet = model
        self.__allPlaces: [PetriNet.Place] = []
        self.__allTransitions: [PetriNet.Transition] = []
        self.initialize_components()

    def get_model(self):
        return self.__model

    def get_initial_marking(self):
        im = Marking()
        for p in self.__model.places:
            if len(p.in_arcs) == 0:
                im[p] = 1
        return im

    def initialize_components(self):
        for t in self.__model.transitions:
            self.__allTransitions.append(t)
        for p in self.__model.places:
            self.__allPlaces.append(p)
        # print(self.__initialPlace)
        # print(self.__finalPlace)
        pass

    def get_transition_by_name(self, name):
        for transition in self.get_model().transitions:
            if transition.name == name:
                return transition
        return None
