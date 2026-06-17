# Global Variable

WINDOW_WORKING_SIZE = (1296, 700) # (h, w) — default for Artale 1282×693

def get_window_working_size(cfg):
    """Compute working size preserving aspect ratio from game content size."""
    content_h, content_w = cfg["game_window"]["size"]  # e.g. [720, 1282] or [693, 1282]
    target_w = 1296
    scale = target_w / content_w
    target_h = int(content_h * scale)
    return (target_w, target_h)
