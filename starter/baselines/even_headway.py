"""Even-Headway baseline controller (Rodriguez et al. style, 0.4*H cap). No trained model needed."""
def even_headway_hold(forward_headway_s, target_headway_s, max_hold_frac=0.4):
    if forward_headway_s >= target_headway_s:
        return 0.0
    return float(min(target_headway_s - forward_headway_s, max_hold_frac * target_headway_s))

class EvenHeadwayController:
    def __init__(self, target_headway_s): self.H = target_headway_s
    def act(self, bus_state): return {"hold_s": even_headway_hold(bus_state["forward_headway_s"], self.H)}

if __name__ == "__main__":
    c = EvenHeadwayController(300)
    for h in (120, 300, 420): print(f"fwd={h}s -> hold {c.act({'forward_headway_s': h})['hold_s']:.0f}s")
