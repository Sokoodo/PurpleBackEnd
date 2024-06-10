from collections import defaultdict

import zope.interface
from pm4py import PetriNet

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.powl.obj import Transition
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.petri_net import semantics, obj

from collections import defaultdict
from purple.log_evaluator.footprint_relations import FootprintRelations


class ILogEvaluator(zope.interface.Interface):
    def evaluate(self, event_log, delta):
        pass


@zope.interface.implementer(ILogEvaluator)
class LogEvaluator:
    def __init__(self):
        pass

    def evaluate(self, event_log, delta):
        pass

    def compare_alpha_relations(self, ref, disc, tau, ref_relations):
        missing = EventLog()

        for ref_act1 in ref:
            if ref_act1 not in disc:  # Activity not yet discovered
                trace = Trace()
                event = Event({'concept:name': ref_act1})
                trace.append(event)
                missing.append(trace)
            else:
                ref_rel = ref[ref_act1]
                for ref_act2, relation in ref_rel.items():
                    if relation == FootprintRelations.SEQUENCE:
                        if ref_act2 not in disc[ref_act1] or disc[ref_act1][ref_act2] in [FootprintRelations.PARALLEL,
                                                                                          FootprintRelations.CHOICE]:
                            trace = Trace()
                            event1 = Event({'concept:name': ref_act1})
                            event2 = Event({'concept:name': ref_act2})
                            trace.append(event1)
                            trace.append(event2)
                            missing.append(trace)
                    elif relation == FootprintRelations.PARALLEL:
                        if ref_act2 not in disc[ref_act1] or disc[ref_act1][ref_act2] == FootprintRelations.CHOICE:
                            trace1 = Trace()
                            event1 = Event({'concept:name': ref_act1})
                            event2 = Event({'concept:name': ref_act2})
                            trace1.append(event1)
                            trace1.append(event2)
                            missing.append(trace1)

                            trace2 = Trace()
                            event3 = Event({'concept:name': ref_act2})
                            event4 = Event({'concept:name': ref_act1})
                            trace2.append(event3)
                            trace2.append(event4)
                            missing.append(trace2)
                        elif disc[ref_act1][ref_act2] == FootprintRelations.SEQUENCE:
                            trace = Trace()
                            event1 = Event({'concept:name': ref_act2})
                            event2 = Event({'concept:name': ref_act1})
                            trace.append(event1)
                            trace.append(event2)
                            missing.append(trace)
                    elif relation == FootprintRelations.CHOICE:
                        if ref_act2 not in disc[ref_act1] or disc[ref_act1][ref_act2] in [FootprintRelations.PARALLEL,
                                                                                          FootprintRelations.SEQUENCE]:
                            trace1 = Trace()
                            event1 = Event({'concept:name': ref_act1})
                            trace1.append(event1)
                            missing.append(trace1)

                            trace2 = Trace()
                            event2 = Event({'concept:name': ref_act2})
                            trace2.append(event2)
                            missing.append(trace2)

        if len(missing) / ref_relations >= tau / 100:
            return None
        return missing

    def get_alpha_relations_from_event_log(self, log):
        matrix = defaultdict(lambda: defaultdict(lambda: None))
        for trace in log:
            for i in range(len(trace) - 1):
                init = trace[i]['concept:name']
                fin = trace[i + 1]['concept:name']
                if matrix[init][fin] is None:
                    matrix[init][fin] = FootprintRelations.SEQUENCE
                else:
                    matrix[fin][init] = None  # This is how we handle the opposite relation

        return matrix

    def get_alpha_relations(self, net: PetriNet):
        transitions: [PetriNet.Transition] = net.transitions
        matrix = {t.label: {} for t in transitions if t.label}
        for t in transitions:
            if not t.label:
                continue
            for next_t in self.get_visible_successors(t, net):
                next_t_name = next_t.label
                if next_t_name:
                    matrix[t.label][next_t_name] = FootprintRelations.SEQUENCE
        print(matrix)
        return matrix

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

    def get_alpha_relations_from_process_tree(self, process_tree):
        matrix = defaultdict(lambda: defaultdict(lambda: None))
        tasks = petri_utils.get_leaves(process_tree)

        for task in tasks:
            task_name = task.name
            if task_name not in matrix:
                matrix[task_name] = defaultdict(lambda: None)

        for task in tasks:
            task_name = task.name
            for successor in task.succeeding_nodes():
                if isinstance(successor, ProcessTree.Task):
                    successor_name = successor.name
                    matrix[task_name][successor_name] = FootprintRelations.SEQUENCE
                elif isinstance(successor, ProcessTree.Gateway):
                    successor_tasks = self.find_successor_tasks(successor)
                    for succ_task in successor_tasks:
                        matrix[task_name][succ_task.name] = FootprintRelations.SEQUENCE

        return matrix

    def find_successor_tasks(self, gateway):
        tasks = set()
        for successor in gateway.succeeding_nodes():
            if isinstance(successor, ProcessTree.Task):
                tasks.add(successor)
            elif isinstance(successor, ProcessTree.Gateway):
                tasks.update(self.find_successor_tasks(successor))
        return tasks

    def compare_alpha_relations(self, ref, disc, tau, ref_relations):
        missing = []
        for ref_act1 in ref:
            if ref_act1 not in disc:  # Activity not yet discovered
                missing.append([ref_act1])
            else:
                ref_rel = ref[ref_act1]
                for ref_act2, relation in ref_rel.items():
                    if relation == FootprintRelations.SEQUENCE:
                        if ref_act2 not in disc[ref_act1] or disc[ref_act1][ref_act2] in [FootprintRelations.PARALLEL,
                                                                                          FootprintRelations.CHOICE]:
                            missing.append([ref_act1, ref_act2])
                    elif relation == FootprintRelations.PARALLEL:
                        if ref_act2 not in disc[ref_act1] or disc[ref_act1][ref_act2] == FootprintRelations.CHOICE:
                            missing.append([ref_act1, ref_act2])
                            missing.append([ref_act2, ref_act1])
                        elif disc[ref_act1][ref_act2] == FootprintRelations.SEQUENCE:
                            missing.append([ref_act2, ref_act1])
                    elif relation == FootprintRelations.CHOICE:
                        if ref_act2 not in disc[ref_act1] or disc[ref_act1][ref_act2] in [FootprintRelations.PARALLEL,
                                                                                          FootprintRelations.SEQUENCE]:
                            missing.append([ref_act1])
                            missing.append([ref_act2])

        if len(missing) / ref_relations >= tau / 100:
            return None
        return missing
