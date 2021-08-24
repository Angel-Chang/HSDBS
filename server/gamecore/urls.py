from django.conf.urls import url, include
from django.urls import path
from gamecore.views import *

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    #url('', views.index, name='index'),
    # Used for browsable API 
    #url(r'', include(router.urls)),
    # Game realted views
    path('new_player/', AddPlayerView.as_view()),
    path('playerbyname/<str:nick_name>/', PlayerByNicknameDetailView.as_view()),
    path('playerbyline/<str:line_id>/', PlayerByLineDetailView.as_view()),
    path('player/<int:pk>/', PlayerDetailView.as_view()),
 
    path('new_ip/', AddIPView.as_view()),
    path('all_ipList/', AllIPListView.as_view()),
    path('all_ipList/<str:ip_type>/', AllIPListByTypeView.as_view()),
    path('ipList/<int:player_id>/<str:ip_type>/', IPListView.as_view()),
    path('ipList/<int:player_id>/<str:ip_type>/<str:start_date>/<str:end_date>/', IPListWithDateView.as_view()),

    path('add_value/',AddValueView.as_view()),
    path('add_value_List/<str:type>/',AddValueListView.as_view()),
    path('add_value_List/<int:player_id>/<str:type>/',PlayerAddValueListView.as_view()),
    path('add_value_List/<int:player_id>/<str:type>/<str:start_date>/<str:end_date>/',PlayerAddValueListWithDateView.as_view()),

    path('gold_flow/',AddGoldFlowView.as_view()),
    path('gold_flow_List/<str:type>/',GoldFlowListView.as_view()),
    path('gold_flow_List/<str:type>/<str:start_date>/<str:end_date>/',GoldFlowListWithDateView.as_view()),

    path('gold_flow_summary/',GoldFlowSummaryView.as_view()),

    path('player_transfer/',AddPlayerTransferView.as_view()),
    path('sender_transfer/<int:player_id>/<int:jewel_type>/',SenderTransferListView.as_view()),
    path('receiver_transfer/<int:player_id>/<int:jewel_type>/',ReceiverTransferListView.as_view()),
    path('sender_transfer/<int:player_id>/<str:start_date>/<str:end_date>/<int:jewel_type>/',SenderTransferListWithDateView.as_view()),
    path('receiver_transfer/<int:player_id>/<str:start_date>/<str:end_date>/<int:jewel_type>/',ReceiverTransferListWithDateView.as_view()),

    path('player_gold/',AddPlayerGoldView.as_view()),
    path('player_gold_Listbytype/<int:player_id>/<str:type>/',PlayerGoldListView.as_view()),
    path('player_gold_Listbytype/<int:player_id>/<str:type>/<str:start_date>/<str:end_date>/',PlayerGoldListWithDateView.as_view()),

    path('game_room/',AddGameRoomView.as_view()),
    path('game_room/<int:pk>/',GameRoomDetailView.as_view()),
    path('game_room_List/<str:room>/',GameRoomListView.as_view()),
    path('game_room_List/<str:room>/<str:start_date>/<str:end_date>/',GameRoomListWithDateView.as_view()),
 
    path('game_run/',AddGameRunView.as_view()),
    path('game_run/<str:run_id>/',GameRunDetailView.as_view()),
    path('game_run_List/<str:game_room_id>/',GameRunListView.as_view()),
    path('game_run_List/<str:game_room_id>/<str:start_date>/<str:end_date>/',GameRunListWithDateView.as_view()),

    path('agent/',AddAgentView.as_view()),
    path('agent/<int:agent_player_id>/',AgentDetailView.as_view()),

    # 玩家綁定邀請碼
    path('player_bind/<int:player_id>/<str:bindcode>/', PlayerBindView.as_view()),
    # 玩家購買配套
    path('vip_store_value/<int:player_id>/<int:vip_type>/', VipStoredValueView.as_view()),
    # 取得玩家的金幣及鑽石
    path('get_player_jewels/<int:player_id>/', PlayerJewelView.as_view()),

    # 玩家出金申請
    path('player_order/',AddPlayerOrderView.as_view()),
    # 玩家出金申請紀錄
    path('player_order_List/<int:player_id>/',PlayerOrderListView.as_view()),

    # 玩家鑽石紀錄
    path('player_star_List/<int:player_id>/<str:type>/',PlayerStarListView.as_view()),
    path('player_star_ListbyDate/<int:player_id>/<str:type>/<str:start_date>/<str:end_date>/',PlayerStarListWithDateView.as_view()),

    # 取得下線列表
    #path('player_member_list/<int:player_id>/',PlayerMemberListView.as_view()),
    path('player_member_list/<int:player_id>/',player_member_list, name='player_member_list'),

    # 取得特定玩家的粉絲總人數
    #path('player_fans_count/<int:player_id>/<int:vip_type>/',PlayerFansCountView.as_view()),
    path('player_fans_count/<int:player_id>/<int:vip_type>/',player_fans_count, name='player_fans_count'),

    # 取得特定玩家特定配套的直推
    #path('player_member_count/<int:player_id>/<int:vip_type>/',PlayerMemberCountView.as_view()),
    path('player_member_count/<int:player_id>/<int:vip_type>/',player_member_count, name='player_member_count'),

    # 取得特定玩家特定配套的組織圖統計數據
    #path('player_vip_summary/<int:player_id>/<int:vip_type>/',PlayerVipSummaryView.as_view()),
    path('player_vip_summary/<int:player_id>/<int:vip_type>/',player_vip_summary, name='player_vip_summary'),

    # 取得每一個VIP等級的總人數
    #path('vip_count/<int:vip_type>/',VipCountView.as_view()),
    path('vip_count/<int:vip_type>/',vip_count, name='vip_count'),

    # 登入檢查
    path('check_login/<str:user_account>/<str:user_password>/<int:login_system>/',CheckLoginView.as_view()),

    # 玩家購買籌碼
    path('player_buychips/<int:player_id>/<int:amount>/', PlayerBuyChipsView.as_view()),
    # 玩家贖回籌碼
    path('player_redeem/<int:player_id>/<int:amount>/',PlayerRedeemView.as_view()),
    # 玩家贖回籌碼(不抽水)
    path('player_redeem_no_bonus/<int:player_id>/<int:amount>/',PlayerRedeemNoBounsView.as_view()),

    # 玩家見點獎金及匹配獎金紀錄
    path('player_bonus_List/<int:player_id>/<str:type>/',PlayerBonusListView.as_view()),
    path('player_bonus_ListbyDate/<int:player_id>/<str:type>/<str:start_date>/<str:end_date>/',PlayerBonusListWithDateView.as_view()),

    # test
    path('updatebindPlayer/', updatebindPlayer),
    path('cleardata/', cleardata),
    # path('test1/', test1),
]