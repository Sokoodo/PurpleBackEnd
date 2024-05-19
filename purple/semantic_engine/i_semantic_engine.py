import zope.interface


class ISemanticEngine(zope.interface.Interface):
    def get_model(self):
        pass

    def get_initial_state(self):
        pass

    def find_initial_and_final_state(self):
        pass

    def get_next_step(self, old_place):
        pass
