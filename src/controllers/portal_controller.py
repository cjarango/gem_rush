from core import Player
from core.portal import Portal

class PortalController:
    def __init__(self, player: Player, portal: Portal):
        self.player = player
        self.portal = portal

    def try_activate(self) -> dict:
        if self.portal.is_activated():
            return {"success": False, "message": "The portal is already activated."}

        if not self.portal.can_activate(self.player.inventory):
            return {"success": False, "message": "You don't have enough obsidian gems to activate the portal."}

        if self.portal.activate(self.player.inventory):
            return {"success": True, "message": "Portal activated successfully!"}

        return {"success": False, "message": "The portal could not be activated."}
