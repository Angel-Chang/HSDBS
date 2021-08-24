from django.conf.urls import url, include
from django.urls import path
#from django.contrib.auth.decorators import login_required

from member.views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# app_name = 'member'
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', index, name='index'),
    # 公司抽水紀錄
    path('commission', CommissionView.as_view(), name='commission'),
    path('bonus_list/', bonus_list, name='bonus_list'),
    path('bonus_detail/', bonus_detail, name='bonus_detail'),

    # 系統金流管理
    path('goldflow/', goldflow, name='goldflow'),
    path('addGold/', addGold, name='addGold'),

    # 出金申請
    path('player_order/', player_order, name='player_order'),
    # 將出金申請從審查中改為已出金
    path('update_player_order/',update_player_order, name='update_player_order'),

    # 玩家資訊-玩家列表
    path('playerlist/', playerlist, name='playerlist'),
    path('player/', player, name='player'),
    path('modify_player_type/', modify_player_type, name='modify_player_type'),
    path('addvalue/', addvalue, name='addvalue'),

    # 玩家資訊-VIP組織圖
    path('vip/', vip, name='vip'),
    path('vipseat/', vipseat, name='vipseat'),

    # 遊戲資訊-牌局紀錄
    path('game_room/', game_room, name='game_room'),
    # 遊戲資訊-牌局紀錄-詳細
    path('gameroom_detail/', gameroom_detail , name='gameroom_detail'),
    # 遊戲資訊-玩家戰績
    path('show_score/', show_score, name='show_score'),
    # 遊戲資訊-玩家排行
    path('leaderboard/', leaderboard, name='leaderboard'),

    # 公告管理
    path('bulletin', BulletinView.as_view(), name='bulletin'),
    path('sendmail/', sendmail, name='sendmail'),

    # 公司報表相關專區
    path('block_list/', block_list , name='block_list'),

    # 管理員資訊-管理員清單
    path('admin_list/', admin_list, name='admin_list'),
    path('account/', account, name='account'),
    path('delete_account/',DeleteAccountView.as_view(), name='delete_account'),

    # 管理員資訊-修改密碼
    path('password_change/', password_change, name='password_change'),
    
    # 登入
    path('login/', login, name='login'),
    # 登出
    path('logout/', logout, name='logout'),
    
    # 玩家後台系統專用 start --------------------------------------------------
    path('playerindex/', playerindex, name='playerindex'),
    # 玩家資訊
    path('player1/', player1, name='player1'),
    # VIP組織圖
    path('playervip/', playervip, name='playervip'),
    path('playervipseat/', playervipseat, name='playervipseat'),
    # 登入
    path('playerlogin/', playerlogin, name='playerlogin'),
    # 登出
    path('playerlogout/', playerlogout, name='playerlogout'),

]