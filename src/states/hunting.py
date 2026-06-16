from src.states.base_state import State

class HuntingState(State):
    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def check_transitions(self):
        # Rune system: only check when enabled (disabled for Talery)
        if self.bot.cfg.get("rune", {}).get("enable", True):
            if self.bot.rune_solver.is_rune_enable(
                self.bot.img_frame_gray, self.bot.img_frame_debug) or \
                self.bot.rune_solver.is_rune_warning(
                self.bot.img_frame_gray, self.bot.img_frame_debug):
                # When "Rune enable" message appears on screen
                self.bot.screenshot_img_frame()

                return "finding_rune"

        # Anti-cheat: check for Talery verification popup
        if self.bot.cfg.get("talery_anti_cheat", {}).get("enable", False):
            # TODO: add actual anti-cheat detection when Talery mechanism is known
            pass

        return None

    def on_frame(self):
        # Get commend from route map
        self.bot.update_cmd_by_route()

        # Check if reach goal on route map
        self.bot.check_reach_goal()

        # Get attack commend by detecting mobs near players
        self.bot.update_cmd_by_mob_detection()

        # If player stuck for too long, perform a random command
        if self.bot.is_player_stuck():
            self.bot.update_cmd_by_random()

        # send command to keyboard controller
        self.bot.kb.set_command(self.bot.cmd_move_x + ' ' + \
                                self.bot.cmd_move_y + ' ' + \
                                self.bot.cmd_action)
