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

    def get_next_transitions(self, old_element: PetriNet.Place):
        transitions: [PetriNet.Transition] = []
        print(old_element)
        for t in self.__model.transitions:
            for in_arc in t.in_arcs:
                if str(old_element.name) == str(in_arc.source.name):
                    transitions.append(t)

        # if len(transitions) != 0:
        #     return transitions[0]
            # for t in transitions:
            #     pass
                # print("trans=" + t)

        return transitions[0] if len(transitions) > 0 else None

    def get_next_places(self, old_element: PetriNet.Transition):
        places: [PetriNet.Place] = []

        for p in self.__model.places:
            for in_arc in p.in_arcs:
                if str(old_element.name) == str(in_arc.source.name):
                    places.append(p)

        strCom = ''
        if len(places) != 0:
            for p in places:
                pass
                # strCom = strCom + p
        # print("plc=" + strCom)

        return places

    def get_next_step(self, prefix):
        pass