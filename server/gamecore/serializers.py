from django.contrib.auth.models import User, Group
from django.conf import settings
from rest_framework import serializers
from gamecore.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

# 玩家資訊        
class PlayerSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Player
        fields = [
            'id', 'nick_name', 'line_id', 'line_profile_url', 
            'real_name', 'phone_number', 'permission_type', 
            'is_lock', 'gold_total', 
            'score', 'email', 'register_mac_addr', 'register_imei',
            'linkcode', 'bindcode', 'bind_player'
        ]

class UpdatePlayerSerializer(serializers.HyperlinkedModelSerializer):
    vip_name = serializers.CharField(label='等級稱號', source ='get_vip_type_display')
    class Meta:
        model = Player
        fields = [
            'id', 'nick_name', 'line_id', 'line_profile_url', 
            'real_name', 'phone_number', 'permission_type', 'is_lock',
            'gold_total', 'score', 'email',
            'register_mac_addr', 'created_date', 'linkcode', 'bindcode',
            'vip_name', 'star', 'bind_player'
        ]

class IPSerializer(serializers.HyperlinkedModelSerializer):
    player_id = serializers.IntegerField(label='玩家ID')
    
    class Meta:
        model = IPInfo
        fields = ['id', 'player_id', 'ip', 'created_date', 'type', 'mac_addr','imei']

class AddValueSerializer(serializers.HyperlinkedModelSerializer):
    player_id = serializers.IntegerField(label='玩家ID')
    created_date = serializers.DateTimeField(format=settings.DATETIME_FORMAT, required=False)

    class Meta:
        model = AddValue
        # fields = ['id', 'player_id', 'type', 'gold', 
        #           'description', 'admin_account', 'created_date', 'old_gold']
        fields = ['id', 'player_id', 'type', 'gold', 
                  'description', 'admin_account', 'old_gold']

class GoldFlowSerializer(serializers.HyperlinkedModelSerializer):
    target_player_id = serializers.IntegerField(label='目標玩家ID')
    created_date = serializers.DateTimeField(label='異動時間',format=settings.DATETIME_FORMAT, required=False)
    amount = serializers.DecimalField(label='異動金額',max_digits=20, decimal_places=2)

    class Meta:
        model = GoldFlow
        fields = ['id', 'target_player_id', 
                  'type', 'amount', 'created_date', 
                  'admin_account','old_amount']

class GoldFlowSummarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoldFlowSummary
        fields = ['total_amount', 'available_amount', 'flow_amount']

class PlayerTransferSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TransferGold
        fields = ['id','sender_id', 'receiver_id', 'amount',
                  'sender_gold','receiver_gold','jewel_type']

class PlayerTransferListSerializer(serializers.HyperlinkedModelSerializer):
    created_date = serializers.DateTimeField(label='異動時間',format=settings.DATETIME_FORMAT, required=False)

    class Meta:
        model = TransferGold
        fields = ['id','sender_id', 'receiver_id', 'amount', 'created_date','jewel_type']

# 玩家金流紀錄
class PlayerGoldSerializer(serializers.HyperlinkedModelSerializer):
    player_id = serializers.IntegerField(label='玩家ID')
    created_date = serializers.DateTimeField(label='異動時間',format=settings.DATETIME_FORMAT, required=False)

    class Meta:
        model = PlayerGold
        fields = ['id','player_id', 'type', 'amount', 'created_date', 'old_amount']

# 牌局紀錄
class GameRoomSerializer(serializers.HyperlinkedModelSerializer):
    start_date = serializers.DateTimeField(label='異動時間',format=settings.DATETIME_FORMAT, required=False)

    class Meta:
        model = GameRoom
        fields = ['id', 'room', 'room_create_date', 'area', 
                  'state', 'base',  'points', 'start_date', 
                  'total_commission']

class GameRoomDetailSerializer(serializers.HyperlinkedModelSerializer):
    start_date = serializers.DateTimeField(format=settings.DATETIME_FORMAT, required=False)

    class Meta:
        model = GameRoom
        fields = ['id', 'room', 'room_create_date', 'area', 
                  'state', 'base', 'points', 'start_date', 
                  'total_commission', 'created_date',
                  'last_modify_date']

# 場局紀錄
class GameRunSerializer(serializers.HyperlinkedModelSerializer):
    game_room_id = serializers.IntegerField(label='牌局紀錄PK值')

    class Meta:
        model = GameRun
        fields = ['run_id', 'game_room_id','seqno', 'seqno_start_date', 
                  'run_name', 'base', 'points', 'player1', 'player2', 
                  'player3', 'player4', 'win_player', 'lost_won_player', 
                  'win_self_hand_player', 'player1_win', 'player2_win',
                  'player3_win', 'player4_win', 'banker_player']

# 場局紀錄
class GameRunDetailSerializer(serializers.HyperlinkedModelSerializer):
    game_room_id = serializers.IntegerField(label='牌局紀錄PK值')

    class Meta:
        model = GameRun
        fields = ['run_id', 'game_room_id','seqno', 'seqno_start_date', 
                  'run_name', 'base', 'points', 'player1', 'player2', 
                  'player3', 'player4', 'win_player', 'lost_won_player', 
                  'win_self_hand_player', 'created_date', 'last_modify_date',
                  'player1_start_gold', 'player2_start_gold',
                  'player3_start_gold', 'player4_start_gold',
                  'player1_win', 'player2_win', 'player3_win', 'player4_win',
                  'banker_player', 'player1_settle_gold', 'player2_settle_gold',
                  'player3_settle_gold', 'player4_settle_gold']

# 代理紀錄
class AgentSerializer(serializers.HyperlinkedModelSerializer):
    agent_player_id = serializers.IntegerField(label='代理玩家ID')
    class Meta:
        model = AgentInfo
        fields = ['id', 'agent_player_id', 'commisson_pc', 'remain_commisson', 
                  'child_player_count', 'child_player_total_run', 
                  'child_agent_player']

# 代理紀錄
class UpdateAgentSerializer(serializers.HyperlinkedModelSerializer):
    agent_player_id = serializers.IntegerField(label='代理玩家ID')
    class Meta:
        model = AgentInfo
        fields = ['id', 'agent_player_id', 'commisson_pc',  'remain_commisson', 
                  'child_player_count', 'child_player_total_run', 
                  'child_agent_player', 'created_date', 'last_modify_date']
# 使用者帳號
class NewAccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id', 'user_account', 'user_password', 'user_name', 
            'phone_number', 'level', 'player_id', 'create_user'
        ]

class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id', 'user_account', 'user_name', 'phone_number', 
            'level', 'player_id', 'create_user', 'created_date', 
            'last_login_date', 'is_delete'
        ]

class ChangePasswordSerializer(serializers.HyperlinkedModelSerializer):
    old_password = serializers.CharField(label='舊密碼', max_length=20)
    new_password = serializers.CharField(label='新密碼', max_length=20)
    class Meta:
        model = Account
        fields = ['id', 'user_account', 'old_password', 'new_password', 'modify_user']
'''
 為用到前端的資料各自建立對應的serializer
 功能：公司抽水紀錄 
   1.某月每日的抽水紀錄列表
   2.某日的每小時抽水紀錄列表
'''   
class newGoldFlowSerializer(serializers.HyperlinkedModelSerializer):
  '''
  GOLD_FLOW_CATEGORY = (
      ("1", "發行金幣"),
      ("2", "補償"),
      ("3", "信用卡儲值"),
      ("4", "介紹金"),
      ("5", "抽水"),
      ("6", "體驗金"),
  )
  type =
  ''' 
  target_player_id = serializers.IntegerField(label='目標玩家ID')
  created_date = serializers.DateTimeField(label='異動時間',format=settings.DATE_FORMAT1, required=False)
  amount = serializers.DecimalField(label='異動金額',max_digits=20, decimal_places=2)

  class Meta:
    model = GoldFlow
    fields = ['id', 'target_player_id', 'type', 'amount', 'created_date','admin_account']

'''
  公司報表 - 封鎖清單
'''
class newBlockListSerializer(serializers.HyperlinkedModelSerializer):
  at_id = serializers.CharField(label='ID', source='get_at_id')
  gold_total = serializers.DecimalField(max_digits=20, decimal_places=2)
  bind_player_name = serializers.SerializerMethodField(label='推薦人姓名')
  total_run = serializers.SerializerMethodField(label='歷史場數')
  average_run = serializers.SerializerMethodField(label='日平均場')
  last_login_date = serializers.DateTimeField(label='最後登入時間',format=settings.DATETIME_FORMAT, required=False)
  created_date = serializers.DateTimeField(label='註冊時間',format=settings.DATETIME_FORMAT)
  permission = serializers.CharField(label='身份', source ='get_permission_type_display')
  abs_score = serializers.SerializerMethodField(label='分數')

  class Meta:
    model = Player
    fields = [
        'at_id', 'nick_name', 'gold_total', 'phone_number', 'register_mac_addr',
        'total_run', 'average_run',
        'score', 'abs_score', 'last_login_date', 'created_date', 
        'permission_type', 'permission', 'bind_player_name'
    ]

  def get_bind_player_name(self, obj):
    try:
      matchedPlayer = Player.objects.get(pk = obj.bind_player)
      return matchedPlayer.nick_name

    except Player.DoesNotExist:
      return ""

  # 歷史場數
  def get_total_run(self, obj):
    total_run = 0

    return total_run

  # 日平均場
  def get_average_run(self, obj):
    average_run = 0
    return average_run

  def get_abs_score(self, obj):
    return abs(obj.score)

'''
  管理員資訊 - 管理員清單
'''
class newAdminListSerializer(serializers.HyperlinkedModelSerializer):
  level_name = serializers.CharField(label='身份', source ='get_level_display')
  last_login_date = serializers.DateTimeField(label='最後登入時間',format=settings.DATETIME_FORMAT, required=False)
  operate = serializers.SerializerMethodField(label='設定') 

  class Meta:
    model = Account
    fields = [
      'id', 'user_account', 'user_name', 'phone_number', 
      'level', 'level_name', 'last_login_date', 'operate'
    ]

  def get_operate(self, obj):
    return ''

'''
  for 玩家綁定邀請碼
'''      
class PlayerBindSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Player
        fields = [
            'id', 'bindcode'
        ]

'''
  for VIP 儲值
'''      
class VipStoredValueSerializer(serializers.HyperlinkedModelSerializer):
    vip_name = serializers.CharField(label='等級稱號', source ='get_vip_type_display')

    class Meta:
        model = Player
        fields = [
            'id', 'gold_total', 'vip_type', 'vip_name'
        ]

'''
  for 取得玩家的金幣及鑽石
'''      
class PlayerJewelViewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = [
            'id', 'gold_total', 'star'
        ]

'''
  for 玩家出金紀錄
''' 
class PlayerOrderSerializer(serializers.HyperlinkedModelSerializer):
    player_id = serializers.IntegerField(label='玩家ID')
    class Meta:
        model = PlayerOrder
        fields = ['id','player_id', 'wallet_addr', 'amount']

class PlayerOrderListSerializer(serializers.HyperlinkedModelSerializer):
    player_id = serializers.IntegerField(label='玩家ID')
    created_date = serializers.DateTimeField(label='日期',format=settings.DATETIME_FORMAT, required=False)
    status_desc = serializers.CharField(label='狀態', source ='get_status_display')

    class Meta:
        model = PlayerOrder
        fields = ['id','player_id', 'wallet_addr', 'amount',
                  'status','status_desc','created_date']

# 玩家鑽石紀錄
class PlayerStarSerializer(serializers.HyperlinkedModelSerializer):
    player_id = serializers.IntegerField(label='玩家ID')
    star_desc = serializers.CharField(label='種類說明', source ='get_star_type_display')    
    created_date = serializers.DateTimeField(label='日期',format=settings.DATETIME_FORMAT, required=False)

    class Meta:
        model = PlayerStar
        fields = ['id','player_id', 'star_type', 'star_desc', 'star', 'created_date']