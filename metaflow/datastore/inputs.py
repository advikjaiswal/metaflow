def __init__(self, flows):

    def get_foreach_index(flow):
        try:
            return flow._foreach_stack[-1]
        except (AttributeError, IndexError):
            return 0

    flows = list(flows)  # ← restore safety
    self.flows = sorted(flows, key=get_foreach_index)

    for flow in self.flows:
        setattr(self, flow._current_step, flow)
