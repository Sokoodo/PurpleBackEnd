import math
import random
from copy import deepcopy
from datetime import datetime, timedelta

import zope.interface
from pm4py.objects.log.obj import EventLog, Trace, Event

from purple.evaluator.log_evaluator.i_log_evaluator import ILogEvaluator


@zope.interface.implementer(ILogEvaluator)
class CnLogEvaluator:
    def __init__(self, traces_number: int, missing_head: int, missing_tail: int, missing_episode: int,
                 order_perturbation: int, alien_activities: int):
        self._traces_number = traces_number
        (self._missing_head_nr, self._missing_tail_nr, self._missing_episode_nr, self._order_perturbation_nr,
         self._alien_activities_nr, self._tot_noisy_traces) = (
            self.calculate_percentages(missing_head, missing_tail, missing_episode,
                                       order_perturbation, alien_activities))

    def calculate_percentages(self, missing_head, missing_tail, missing_episode, order_perturbation, alien_traces):
        # Avoid dividing by zero
        if self._traces_number > 0:
            missing_head_traces: int = math.floor((missing_head / 100) * self._traces_number)
            missing_tail_traces: int = math.floor((missing_tail / 100) * self._traces_number)
            missing_episode_traces: int = math.floor((missing_episode / 100) * self._traces_number)
            order_perturbation_traces: int = math.floor((order_perturbation / 100) * self._traces_number)
            alien_traces_traces: int = math.floor((alien_traces / 100) * self._traces_number)
            sum_noisy_traces: int = missing_head_traces + missing_tail_traces + missing_episode_traces + order_perturbation_traces + alien_traces
            return (missing_head_traces, missing_tail_traces, missing_episode_traces, order_perturbation_traces,
                    alien_traces_traces, sum_noisy_traces)
        else:
            raise ValueError("The number of traces must be greater than zero.")

    def evaluate(self, traces: list):
        index_to_count = 0
        event_log = EventLog()

        missing_head_traces = traces[index_to_count:index_to_count + self._missing_head_nr]
        index_to_count += self._missing_head_nr
        for trace in self.createHeadTraces(missing_head_traces):
            event_log.append(trace)

        missing_tail_traces = traces[index_to_count:index_to_count + self._missing_tail_nr]
        index_to_count += self._missing_tail_nr
        for trace in self.createTailTraces(missing_tail_traces):
            event_log.append(trace)

        missing_episode_traces = traces[index_to_count:index_to_count + self._missing_episode_nr]
        index_to_count += self._missing_episode_nr
        for trace in self.createEpisodeTraces(missing_episode_traces):
            event_log.append(trace)

        order_perturbation_traces = traces[index_to_count:index_to_count + self._order_perturbation_nr]
        index_to_count += self._order_perturbation_nr
        for trace in self.createOrderPerturbatedTraces(order_perturbation_traces):
            event_log.append(trace)

        alien_activities_traces = traces[index_to_count:index_to_count + self._alien_activities_nr]
        index_to_count += self._alien_activities_nr
        for trace in self.createAlienTraces(alien_activities_traces):
            event_log.append(trace)

        normal_traces = traces[
                        index_to_count:index_to_count + (self._traces_number - math.floor(self._tot_noisy_traces))]
        for trace in normal_traces:
            event_log.append(trace)

        return event_log

    def createHeadTraces(self, missing_head_traces) -> [Trace]:
        new_head_traces = []

        for trace in missing_head_traces:
            modified_trace = deepcopy(trace)
            max_removable_events = len(modified_trace) - 1

            if max_removable_events > 0:
                num_events_to_remove = random.randint(1, max_removable_events)
                modified_trace = modified_trace[num_events_to_remove:]

            new_head_traces.append(modified_trace)

        return new_head_traces

    def createTailTraces(self, missing_tail_traces) -> [Trace]:
        new_tail_traces = []

        for trace in missing_tail_traces:
            modified_trace = deepcopy(trace)
            max_removable_events = len(modified_trace) - 1

            if max_removable_events > 0:
                num_events_to_remove = random.randint(1, max_removable_events)
                modified_trace = modified_trace[:-num_events_to_remove]

            new_tail_traces.append(modified_trace)

        return new_tail_traces

    def createEpisodeTraces(self, missing_episode_traces) -> [Trace]:
        new_episode_traces = []

        for trace in missing_episode_traces:
            modified_trace = deepcopy(trace)

            if len(modified_trace) > 2:
                max_removable_events = len(modified_trace) - 2
                num_events_to_remove = random.randint(1, max_removable_events)
                start_index = 1
                end_index = len(modified_trace) - 1
                indices_to_remove = sorted(random.sample(range(start_index, end_index), num_events_to_remove),
                                           reverse=True)
                for index in indices_to_remove:
                    modified_trace._list.pop(index)

            new_episode_traces.append(modified_trace)
        return new_episode_traces

    def createOrderPerturbatedTraces(self, order_perturbation_traces) -> [Trace]:
        new_order_perturbed_traces = []

        for trace in order_perturbation_traces:
            modified_trace = deepcopy(trace)
            max_swaps = len(modified_trace) // 2
            num_swaps = random.randint(1, max_swaps)
            indices = list(range(len(modified_trace) - 1))

            for _ in range(num_swaps):
                if len(indices) < 2:
                    break
                idx1 = random.choice(indices)
                idx2 = idx1 + 1

                modified_trace[idx1], modified_trace[idx2] = modified_trace[idx2], modified_trace[idx1]

                indices.remove(idx1)
                if idx2 in indices:
                    indices.remove(idx2)

            new_order_perturbed_traces.append(modified_trace)

        return new_order_perturbed_traces

    def createAlienTraces(self, alien_activities_traces) -> [Trace]:
        new_alien_traces = []

        for i, trace in enumerate(alien_activities_traces):
            temp_trace = deepcopy(trace)
            max_alien_events = max(len(temp_trace) - 2, 1)  # Ensure max_alien_events is at least 1

            # We want to generate at least 1 alien event
            num_alien_events = random.randint(1, max_alien_events)

            alien_events = []
            # Generate alien events
            for j in range(num_alien_events):
                new_alien_event = Event({
                    "concept:name": f"AlienEvent_{j + 1}",
                    "time:timestamp": datetime.now() + timedelta(seconds=i * 60 + j),
                    "marking": ""
                })
                alien_events.append(new_alien_event)

            # Insert alien events at random positions within the trace
            for new_alien_event in alien_events:
                if len(temp_trace) > 1:
                    # Ensure position is between 1 and len(temp_trace) - 1
                    position = random.randint(1, len(temp_trace) - 1)
                    temp_trace.insert(position, new_alien_event)

            new_alien_traces.append(temp_trace)

        return new_alien_traces
