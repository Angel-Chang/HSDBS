# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

# Hide the header 
admin.site.site_header = " "
admin.site.site_title = "星濠娛樂 Admin"
admin.site.site_url = None 
admin.site.index_title = " "

class PurchaseDataAdmin(admin.ModelAdmin):
    pass
    def has_change_permission(self, request, obj=None):
        return True
    def has_view_permission(self, request, obj=None):
        return True
    def has_add_permission(self, request):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_module_permission(self, request):
        return True

class PlayerDataAdmin(admin.ModelAdmin):
    pass
    def has_change_permission(self, request, obj=None):
        return True
    def has_view_permission(self, request, obj=None):
        return True
    def has_add_permission(self, request):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_module_permission(self, request):
        return True

class ClubDataAdmin(admin.ModelAdmin):
    pass
    def has_change_permission(self, request, obj=None): 
        return True
    def has_view_permission(self, request, obj=None):
        return True
    def has_add_permission(self, request):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_module_permission(self, request):
        return True

'''
admin.site.register(PurchaseData, PurchaseDataAdmin)
'''
#admin.site.register(Player, PlayerDataAdmin)

admin.site.register(Player)
admin.site.register(IPInfo)
admin.site.register(GameCategory)
admin.site.register(AddValue)
admin.site.register(GoldFlow)
admin.site.register(GoldFlowSummary)
admin.site.register(TransferGold)
admin.site.register(PlayerGold)
admin.site.register(GameRoom)
admin.site.register(GameRun)
admin.site.register(AgentInfo)
admin.site.register(Account)
admin.site.register(LoginInfo)
admin.site.register(PlayerGameRoom)
admin.site.register(PlayerRoundResult)
admin.site.register(Bulletin)
admin.site.register(StarFlow)
admin.site.register(PlayerStar)
admin.site.register(PlayerOrder)
admin.site.register(VIPTree)
admin.site.register(VIPBonus)
admin.site.register(VIPSeqn)
