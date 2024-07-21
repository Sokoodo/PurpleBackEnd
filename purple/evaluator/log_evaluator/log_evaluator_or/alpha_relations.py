from collections import defaultdict

from pm4py import PetriNet
from pm4py.objects.log.obj import EventLog, Trace, Event

from purple.evaluator.log_evaluator.footprint_relations import FootprintRelations


class AlphaRelations:
    def __init__(self):
        pass

    def get_footprint_matrix_from_petri(self, net: PetriNet):
        transitions: [PetriNet.Transition] = net.transitions
        matrix = {t.label: {} for t in transitions if t.label}
        for t in transitions:
            if not t.label:
                continue
            for next_t in self.get_visible_successors(t, net):
                next_t_name = next_t.label
                if next_t_name:
                    matrix[t.label][next_t_name] = FootprintRelations.SEQUENCE
        return matrix

    def get_footprint_matrix_from_event_log(self, log: EventLog):
        footprint_matrix = defaultdict(dict)

        for trace in log:
            events = trace._list
            if len(events) > 1:
                for i in range(len(events) - 1):
                    init = events[i]["concept:name"]
                    successive = events[i + 1]["concept:name"]

                    if successive in footprint_matrix and init in footprint_matrix[successive]:
                        del footprint_matrix[successive][init]
                    else:
                        footprint_matrix[init][successive] = FootprintRelations.SEQUENCE

            elif len(events) == 1: # per evitare errore che si verifica quando c'è solo un evento nel log
                init = events[0]["concept:name"]
                if init not in footprint_matrix:
                    footprint_matrix[init] = {}

        return footprint_matrix

    def compare_footprint_matrices(self, event_log_matrix, petri_net_matrix, tau, ref_relations):
        el_missing = EventLog()

        for event, transitions in petri_net_matrix.items():
            if event not in event_log_matrix: # quà entra quando l'evento non è nella 2a matrice
                if len(transitions) == 0:
                    trace = Trace()
                    trace._list.append(Event({"concept:name": event}))
                    el_missing.append(trace)
                for next_event in transitions:
                    trace = Trace()
                    trace._list.append(Event({"concept:name": event}))
                    trace._list.append(Event({"concept:name": next_event}))
                    el_missing.append(trace)
            else: # quà entra quando l'evento è già nella 2a matrice ma deve comunque controllare se tutte le sue relazioni sono presenti
                for next_event, relation in transitions.items():
                    if next_event not in event_log_matrix[event]:
                        trace = Trace()
                        trace._list.append(Event({"concept:name": event}))
                        trace._list.append(Event({"concept:name": next_event}))
                        el_missing.append(trace)

        print("Compare: Missing relations")
        for trace in el_missing:
            events_str = " -> ".join(event["concept:name"] for event in trace._list)
            print(f"Trace: {events_str}")

        # Da testare quando guided sim funziona
        # if len(el_missing) / ref_relations >= tau / 100:
        #     print(f"{tau / 100}%, sotto al threshold")
        #     return EventLog()
        return el_missing

    def get_visible_successors(self, transition: [PetriNet.Transition], net: PetriNet):
        next_transitions: [PetriNet.Transition] = []
        out_places: [PetriNet.Place] = []
        for out_arc in transition.out_arcs:
            temp_place = self.getPlace(out_arc.target, net.places)
            if temp_place is not None:
                out_places.append(temp_place)
        for op in out_places:
            for out_places_arc in op.out_arcs:
                temp_trans = self.getTransition(out_places_arc.target.name, net.transitions)
                if temp_trans is not None:
                    next_transitions.append(temp_trans)

        visible_successors = [t for t in next_transitions if isinstance(t, PetriNet.Transition) and t.label is not None]

        return visible_successors

    def getPlace(self, place_name, places: [PetriNet.Place]):
        for p in places:
            if str(p.name) == str(place_name):
                return p

    def getTransition(self, transition_name, transitions: [PetriNet.Transition]):
        for t in transitions:
            if str(t.name) == str(transition_name):
                return t
