# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import os

from django.db import models, connection
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import User


def get_image_path(instance, filename):
  return os.path.join('photos', str(instance.id), filename)

class DBRouter:
    """
    A router to control all database operations on models in the
    user application.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'player_data':
            return 'gameserver'

        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write user models go to users_db.
        """
        # if model._meta.app_label == 'user_data':
        #     return 'users_db'
        # elif model._meta.app_label == 'customer_data':
        #     return 'customer_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the user app is involved.
        """
        # if obj1._meta.app_label == 'user_data' or \
        #    obj2._meta.app_label == 'user_data':
        #    return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the default
        database.
        """
        # if app_label == 'user_data':
        #     return db == 'users_db'
        return None

# playerid = 99999999 => 代表官方
# Create your models here.
class Player(models.Model):
  PERMISSION_TYPE = (
      ("1", "一般會員"),
      ("2", "代理會員")
  )
  VIP_TYPE = (
      (0, ""),
      (1, "賭徒"),
      (2, "賭王"),
      (3, "賭霸"),
      (4, "賭聖"),
      (5, "賭俠"),
      (6, "賭神")
  )
  id = models.AutoField(_("玩家ID"),primary_key=True)

  nick_name = models.CharField(_("暱稱"), max_length=200)
  line_id = models.CharField(_("Line ID"), max_length=200, null=True, blank=True)
  line_profile_url = models.URLField(_("Line 圖片連結"), null=True, blank=True)
  real_name = models.CharField(_("帳號名稱"), max_length=200, null=True, blank=True)
  phone_number = models.CharField(_("手機號碼"),  max_length=15,null=True, blank=True)
  permission_type = models.CharField(_("會員身份"), max_length=1, choices=PERMISSION_TYPE, default='1')
  is_lock = models.BooleanField(_("帳號封鎖？"), default=False)
  gold_total = models.DecimalField(_("金幣"), default=0,max_digits=20, decimal_places=4)
#  gold_total = models.FloatField(_("金幣"), default=0)
  score = models.IntegerField(_("正負分"), default=0)
  email = models.EmailField(_("Email"), max_length=254, null=True, blank=True)
  register_mac_addr = models.CharField(_("MAC位址"), max_length=50, null=True, blank=True)
  register_imei = models.CharField(_("IMEI"), max_length=20, null=True, blank=True)
  created_date = models.DateTimeField(auto_now_add=True)
  last_modify_date = models.DateTimeField(_("最後異動時間"),null=True, blank=True)
  last_login_date = models.DateTimeField(_("最後登入時間"),null=True, blank=True)
  linkcode = models.CharField(_("玩家邀請碼"), max_length=8, default='',null=True, blank=True)
  bindcode = models.CharField(_("綁定邀請碼"), max_length=8, default='',null=True, blank=True)

  # for 獎金制度
  star = models.DecimalField(_("鑽石"), default=0 ,max_digits=20, decimal_places=2)
  #star = models.FloatField(_("鑽石"), default=0)

  vip_type = models.PositiveIntegerField(_("VIP等級"), choices=VIP_TYPE, default=0)

  vip1_seat = models.IntegerField(_("VIP1第一個位置"),default=0)
  vip2_seat = models.IntegerField(_("VIP2第一個位置"),default=0)
  vip3_seat = models.IntegerField(_("VIP3第一個位置"),default=0)
  vip4_seat = models.IntegerField(_("VIP4第一個位置"),default=0)
  vip5_seat = models.IntegerField(_("VIP5第一個位置"),default=0)
  vip6_seat = models.IntegerField(_("VIP6第一個位置"),default=0)

  bind_player = models.PositiveIntegerField(_("推薦人玩家ID"), default = 0)

  def __str__(self):
    return self.nick_name

  def get_at_id(self):
    return f'@{self.id}'

  def get_ref_name(self):
    return f'{self.nick_name}(@{self.id})'

  # 取得推薦人暱稱
  def get_bind_player_name(self):
    try:
      matchedPlayer = Player.objects.get(pk = self.bind_player)
      return matchedPlayer.nick_name
  
    except:
      return ""

  # 取得下一級VIP金額
  def get_next_vip_amount(self):
    if self.vip_type == 0:
      return 10
    elif self.vip_type == 1:
      return 50
    elif self.vip_type == 2:
      return 100
    elif self.vip_type == 3:
      return 500
    elif self.vip_type == 4:
      return 1000
    elif self.vip_type in (5,6) :
      return 2000

  # 利用綁定邀請碼去找推薦人玩家ID
  def get_player_bind_player(self):
      if self.bind_player is not None and self.bind_player > 0:
        return self.bind_player
      
      if self.bindcode is not None and len(self.bindcode) > 0 and self.bindcode != "0":
        try:
          matched = Player.objects.get(linkcode=self.bindcode)
          self.bind_player = matched.id
          self.save()

        except Player.DoesNotExist:
          self.bind_player = 0
          self.save()

      return self.bind_player

  # 查詢玩家某個VIP的首座
  def get_player_firstSeat(self, vip_type):
        if vip_type == 1:
            return self.vip1_seat
        elif vip_type == 2:
            return self.vip2_seat
        elif vip_type == 3:
            return self.vip3_seat
        elif vip_type == 4:
            return self.vip4_seat
        elif vip_type == 5:
            return self.vip5_seat
        elif vip_type == 6:
            return self.vip6_seat

class IPInfo(models.Model):
  IP_TYPE = (
      ("1", "登入"),
      ("2", "開啟新房間"),
      ("3", "離開房間"),
  )

  player = models.ForeignKey(Player, on_delete=models.CASCADE)
  ip = models.GenericIPAddressField()
  type = models.CharField(_("IP Type"),max_length=1, choices=IP_TYPE, default='1')
  mac_addr = models.CharField(_("MAC 位址"),null=True, blank=True, max_length=50)
  imei = models.CharField(_("IMEI"), null=True, blank=True, max_length=20)
  created_date = models.DateTimeField(auto_now_add=True)

class GameCategory(models.Model):
  player = models.OneToOneField(
      Player,
      on_delete=models.CASCADE,
      primary_key=True,
  )
  four_MJ = models.BooleanField(_("四人麻將"),default=False)
  two_MJ = models.BooleanField(_("二人麻將"),default=False)
  niuniu_poker = models.BooleanField(_("牛牛"),default=False)

# 系統補幣紀錄
class AddValue(models.Model):
  CATEGORY = (
      ("2", "補償"),
      ("8", "入金")
  )
  JEWEL_TYPE = (
      (1, "金幣"),
      (2, "鑽石")
  )
  player = models.ForeignKey(Player, on_delete=models.CASCADE)
  type = models.CharField(_("類型"),max_length=1, choices=CATEGORY, default='2')
  gold = models.IntegerField(_("金額"), default=0)
  description = models.CharField(_("說明") , max_length=200, blank=True,default='')
  #admin_account是後台登入的帳號
  admin_account = models.CharField(_("管理者帳號"),max_length=20)
  created_date = models.DateTimeField(auto_now_add=True)
  old_gold = models.DecimalField(_("原始金額/鑽石"), default=0,max_digits=20, decimal_places=4)
  jewel_type = models.PositiveIntegerField(_("貨幣種類"),choices=JEWEL_TYPE,default=1)

  class Meta:
    indexes = [ 
      models.Index(fields=['type','jewel_type','created_date']), 
      ]

# Gold flow record
class GoldFlow(models.Model):
  GOLD_FLOW_CATEGORY = (
      ("1", "發行金幣"),
      ("2", "補幣"),
      ("6", "抽水"),
      ("7", "玩家購買籌碼"),
      ("8", "玩家兌換籌碼")
  )

  type = models.CharField(_("類別"),max_length=1, choices=GOLD_FLOW_CATEGORY, default='2')
  amount = models.DecimalField(_("金額"), default=0,max_digits=20, decimal_places=4)
  target_player = models.ForeignKey(Player,verbose_name=_("目標玩家ID"),on_delete=models.SET_NULL, blank=True,null=True)
  created_date = models.DateTimeField(auto_now_add=True)
  #admin_account是後台登入的帳號
  admin_account = models.CharField(_("管理者帳號"),max_length=20, default='')
  old_amount = models.DecimalField(_("原始金額"), default=0,max_digits=20, decimal_places=4)

  class Meta:
    indexes = [ 
      models.Index(fields=['type','created_date']), 
      ]

# Gold flow summary
class GoldFlowSummary(models.Model):

  total_amount = models.DecimalField(_("發行總金額"), default=0,max_digits=20, decimal_places=4)
  available_amount = models.DecimalField(_("總可用餘額"), default=0,max_digits=20, decimal_places=4)
  flow_amount = models.DecimalField(_("總流動金額"), default=0,max_digits=20, decimal_places=4)
  created_date = models.DateTimeField(auto_now_add=True)
  last_modify_date = models.DateTimeField(_("最後異動時間"),null=True, blank=True)
  star = models.DecimalField(_("鑽石數量"), default=0,max_digits=20, decimal_places=2)

# 轉幣紀錄
class TransferGold(models.Model):
  JEWEL_TYPE = (
      (1, "金幣"),
      (2, "鑽石")
  )
  sender_id = models.PositiveIntegerField(_("贈送人ID"),default=0)
  receiver_id = models.PositiveIntegerField(_("接收人ID"),default=0)
  amount = models.PositiveIntegerField(_("金額"), default=0)
  created_date = models.DateTimeField(auto_now_add=True)
  sender_gold = models.PositiveIntegerField(_("贈送人轉幣前金額"), default=0)
  receiver_gold = models.PositiveIntegerField(_("接收人轉幣前金額"), default=0)
  jewel_type = models.PositiveIntegerField(_("贈送貨幣種類"),choices=JEWEL_TYPE,default=1)

  class Meta:
    indexes = [ 
      models.Index(fields=['jewel_type','sender_id','created_date']), 
      models.Index(fields=['jewel_type','receiver_id','created_date']), 
      ]

# 玩家金流紀錄
class PlayerGold(models.Model):
  CATEGORY = (
      ("1", "購買配套"),
      ("2", "官方補幣"),
      ("3", "贈禮"),
      ("4", "收禮"),
      ("5", "遊戲輸贏"),
      ("6", "抽水"),
      ("7", "購買籌碼"),
      ("8", "兌換籌碼")
  )

  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("玩家ID"))
  type = models.CharField(_("類別"),max_length=2, choices=CATEGORY, default='11')
  amount = models.DecimalField(_("金額"), default=0,max_digits=20, decimal_places=4)
  created_date = models.DateTimeField(auto_now_add=True)
  old_amount = models.DecimalField(_("原始金額"), default=0,max_digits=20, decimal_places=4)
  run_id = models.CharField(_("遊戲局號(回播碼)"), max_length=20 ,null=True, blank=True) 

  class Meta:
    indexes = [ 
      models.Index(fields=['player','type','created_date']), 
      ]

# 牌局紀錄
class GameRoom(models.Model):
  GAME_AREA = (
      ("1", "一般"),
      ("2", "富豪"),
      ("3", "私人"),
  )

  GAME_STATE = (
      ("1", "等待中"),
      ("2", "進行中"),
      ("3", "結束"),
  )

  room = models.CharField(_("房號"), max_length=50)
  room_create_date = models.DateTimeField(_("創建房間時間"),default=timezone.now)
  area = models.CharField(_("區域"), max_length=1, choices=GAME_AREA, default='1')
  state = models.CharField(_("遊戲狀態"), max_length=1, choices=GAME_STATE, default='1')
  base = models.PositiveIntegerField(_("底數"), default=1)
  points = models.PositiveIntegerField(_("台"), default=1)
  start_date = models.DateTimeField(_("遊戲開始時間"),null=True, blank=True)
  total_commission = models.DecimalField(_("總抽水金額"), default=0,max_digits=20, decimal_places=7)
  created_date = models.DateTimeField(auto_now_add=True)
  last_modify_date = models.DateTimeField(_("最後異動時間"),null=True, blank=True)

# 場局紀錄
class GameRun(models.Model):
  run_id = models.CharField(_("遊戲局號(回播碼)"), max_length=20,primary_key=True)
  game_room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
  seqno = models.PositiveSmallIntegerField(_("場次"), default=1)
  seqno_start_date = models.DateTimeField(_("場次開始時間"))
  run_name = models.CharField(_("局"), max_length=10)
  base = models.PositiveIntegerField(_("底數"), default=1)
  points = models.PositiveIntegerField(_("台"), default=1)
  player1 = models.PositiveIntegerField(_("玩家1ID"))
  player2 = models.PositiveIntegerField(_("玩家2ID"))
  player3 = models.PositiveIntegerField(_("玩家3ID"))
  player4 = models.PositiveIntegerField(_("玩家4ID"))
  win_player = models.PositiveIntegerField(_("胡牌"), default=0)
  lost_won_player = models.PositiveIntegerField(_("放槍"), default=0)
  win_self_hand_player = models.PositiveIntegerField(_("自摸"), default=0)
  created_date = models.DateTimeField(auto_now_add=True)
  last_modify_date = models.DateTimeField(_("最後異動時間"),null=True, blank=True)
  player1_start_gold = models.DecimalField(_("玩家ID1起始金額"), default=0,max_digits=20, decimal_places=7)
  player2_start_gold = models.DecimalField(_("玩家ID2起始金額"), default=0,max_digits=20, decimal_places=7)
  player3_start_gold = models.DecimalField(_("玩家ID3起始金額"), default=0,max_digits=20, decimal_places=7)
  player4_start_gold = models.DecimalField(_("玩家ID4起始金額"), default=0,max_digits=20, decimal_places=7)
  player1_win = models.IntegerField(_("玩家ID1成績"), default=0)
  player2_win = models.IntegerField(_("玩家ID2成績"), default=0)
  player3_win = models.IntegerField(_("玩家ID3成績"), default=0)
  player4_win = models.IntegerField(_("玩家ID4成績"), default=0)
  total_bonus = models.DecimalField(_("總官方抽水金額"), default=0,max_digits=20, decimal_places=7)
  banker_player = models.PositiveIntegerField(_("莊家"), default=0)
  player1_settle_gold = models.DecimalField(_("玩家ID1結算金額"), default=0,max_digits=20, decimal_places=7)
  player2_settle_gold = models.DecimalField(_("玩家ID2結算金額"), default=0,max_digits=20, decimal_places=7)
  player3_settle_gold = models.DecimalField(_("玩家ID3結算金額"), default=0,max_digits=20, decimal_places=7)
  player4_settle_gold = models.DecimalField(_("玩家ID4結算金額"), default=0,max_digits=20, decimal_places=7)
  player1_corp_bonus = models.DecimalField(_("玩家ID1官方抽水"), default=0,max_digits=20, decimal_places=7)
  player2_corp_bonus = models.DecimalField(_("玩家ID2官方抽水"), default=0,max_digits=20, decimal_places=7)
  player3_corp_bonus = models.DecimalField(_("玩家ID3官方抽水"), default=0,max_digits=20, decimal_places=7)
  player4_corp_bonus = models.DecimalField(_("玩家ID4官方抽水"), default=0,max_digits=20, decimal_places=7)
  is_settle = models.BooleanField(_("是否已結算過"), default=False)

  def get_area_name(self):
    try:
      matchedRoom = GameRoom.objects.get(pk=self.game_room_id)
      return matchedRoom.get_area_display()

    except:
      return ""

  def get_state_name(self):
    try:
      matchedRoom = GameRoom.objects.get(pk=self.game_room_id)
      return matchedRoom.get_state_display()
    except:
      return ""

# 玩家牌局紀錄1 (後台收到GameRun時處理)
class PlayerGameRoom(models.Model):
  game_room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, verbose_name=_("GameRoomID"))
  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("玩家ID"))
  banker_count = models.IntegerField(_("連莊次數"), default = 0)
  score = models.IntegerField(_("總成績"), default = 0)
  start_gold = models.DecimalField(_("起始金額"), default=0,max_digits=20, decimal_places=4)
  settle_gold = models.DecimalField(_("結算金額"), default=0,max_digits=20, decimal_places=4)
  commission = models.DecimalField(_("官方抽水金額"), default=0,max_digits=20, decimal_places=4)
  created_date = models.DateTimeField(auto_now_add=True)
  last_modify_date = models.DateTimeField(_("最後異動時間"),null=True, blank=True)

# 玩家牌局紀錄2 (後台收到GameRun要結算時處理)
class PlayerRoundResult(models.Model):
  game_run = models.ForeignKey(GameRun, on_delete=models.CASCADE, verbose_name=_("遊戲局號(回播碼)"))
  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("玩家ID"))
  base = models.PositiveIntegerField(_("底數"))
  win = models.PositiveIntegerField(_("胡牌"), default=0)
  lost_won = models.PositiveIntegerField(_("放槍"), default=0)
  win_self_hand = models.PositiveIntegerField(_("自摸"), default=0)
  banker = models.PositiveIntegerField(_("莊家"), default=0)
  score = models.IntegerField(_("成績"), default = 0)
  start_gold = models.DecimalField(_("起始金額"), default=0,max_digits=20, decimal_places=4)
  settle_gold = models.DecimalField(_("結算金額"), default=0,max_digits=20, decimal_places=4)
  corp_bonus = models.DecimalField(_("官方抽水金額"), default=0,max_digits=20, decimal_places=7)
  created_date = models.DateTimeField(auto_now_add=True)

# 代理紀錄
class AgentInfo(models.Model):

  agent_player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("代理玩家ID"))
  commisson_pc = models.DecimalField(_("抽水成數(%)"), default=0,max_digits=10, decimal_places=4)
  remain_commisson = models.DecimalField(_("未領取抽水額"), default=0,max_digits=20, decimal_places=4)
  child_player_count = models.PositiveIntegerField(_("下層玩家數"), default=0)
  child_player_total_run = models.PositiveIntegerField(_("下層玩家總局數"), default=0)
  child_agent_player = models.PositiveIntegerField(_("下層代理數"), default=0)
  created_date = models.DateTimeField(auto_now_add=True)
  last_modify_date = models.DateTimeField(_("最後異動時間"),null=True, blank=True)

# 使用者帳號
class Account(models.Model):
  LEVEL_TYPE = (
      ("1", "代理玩家"),
      ("2", "一般客服"),
      ("3", "客服主管"),
      ("8", "系統主管"),
      ("9", "工程師")
  )
  id = models.AutoField(_("ID"),primary_key=True)

  user_account = models.CharField(_("帳號"), max_length=20)
  user_password = models.CharField(_("密碼"), max_length=20)
  user_name = models.CharField(_("管理員名稱"), max_length=20)
  phone_number = models.CharField(_("手機號碼"),  max_length=15,null=True, blank=True)
  level = models.CharField(_("系統身份"), max_length=1, choices=LEVEL_TYPE, default='8')
  player_id = models.PositiveIntegerField(_("代理玩家ID"), null=True, blank=True)

  create_user = models.CharField(_("創建者帳號"), max_length=20)
  created_date = models.DateTimeField(auto_now_add=True)
  last_login_date = models.DateTimeField(_("最後登入時間"),blank=True,null=True)
  modify_user = models.CharField(_("異動者帳號"),max_length=20)
  last_modify_date = models.DateTimeField(_("最後異動時間"),null=True, blank=True)

  is_delete = models.BooleanField(_("是否被刪除"), default=False)
  deleted_user = models.CharField(_("刪除者帳號"),max_length=20, null=True, blank=True)
  deleted_date = models.DateTimeField(_("帳號刪除時間"),blank=True,null=True)


  def __str__(self):
      return self.user_account

# 登入紀錄
class LoginInfo(models.Model):

  id = models.AutoField(_("ID"),primary_key=True)
  account_id = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_("登入帳號ID"))
  login_system = models.PositiveSmallIntegerField(_("登入系統代碼"), default=1)
  login_date = models.DateTimeField(auto_now=True, verbose_name=_("登入時間"))

# 密碼修改紀錄
class ChangePWDLog(models.Model):

  id = models.AutoField(_("ID"),primary_key=True)
  user_account = models.CharField(_("帳號名稱"), max_length=20)
  old_password = models.CharField(_("舊密碼"), max_length=20)
  new_password = models.CharField(_("新密碼"), max_length=20)
  modify_user = models.CharField(_("異動者帳號名稱"), max_length=20)
  created_date = models.DateTimeField(auto_now=True, verbose_name=_("異動時間"))

# 公告記錄
class Bulletin(models.Model):

  id = models.AutoField(_("ID"),primary_key=True)
  subject = models.CharField(_("主題"), max_length=150)
  message = models.CharField(_("訊息內容"), max_length=500)
  operator = models.CharField(_("操作者名稱"), max_length=20)
  created_date = models.DateTimeField(auto_now=True, verbose_name=_("操作時間"))

# 公告記錄接收者名單
class BulletinReceiver(models.Model):

  id = models.AutoField(_("ID"),primary_key=True)
  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("玩家ID"))
  bulletin = models.ForeignKey(Bulletin, on_delete=models.CASCADE, verbose_name=_("公告記錄ID"))
  email = models.CharField(_("email"), max_length=254, null=True, blank=True)

# 官方鑽石紀錄
class StarFlow(models.Model):
  STARFLOW_TYPE = (
      ("1", "玩家購買配套"),
      ("2", "補幣"),
      ("5", "見點獎金"),
      ("6", "匹配獎金"),
      ("7", "玩家出金"),
      ("8", "入金")
  )

  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("玩家ID"))
  starflow_type = models.CharField(_("類別"),max_length=1, choices=STARFLOW_TYPE, default='1')
  old_star = models.DecimalField(_("未異動前鑽石數量"), default=0,max_digits=20, decimal_places=2)
  star = models.DecimalField(_("異動鑽石數量"), default=0,max_digits=20, decimal_places=2)
  created_date = models.DateTimeField(auto_now_add=True)

  class Meta:
    indexes = [ 
      models.Index(fields=['starflow_type','created_date']), 
      ]

# 玩家鑽石紀錄
class PlayerStar(models.Model):
  STARFLOW_TYPE = (
      ("1", "購買配套"),
      ("2", "官方補幣"),
      ("3", "贈禮"),
      ("4", "收禮"),
      ("5", "見點獎金"),
      ("6", "匹配獎金"),
      ("7", "出金"),
      ("8", "入金")
  )

  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("玩家ID"))
  star_type = models.CharField(_("類別"),max_length=2, choices=STARFLOW_TYPE, default='2')
  obj_playerid = models.PositiveIntegerField(_("對象玩家ID"))
  old_star = models.DecimalField(_("原始鑽石數量"), default=0,max_digits=20, decimal_places=4)
  star = models.DecimalField(_("異動鑽石數量"), default=0,max_digits=20, decimal_places=2)
  created_date = models.DateTimeField(auto_now_add=True)

  class Meta:
    indexes = [ 
      models.Index(fields=['star_type','created_date']), 
      ]

# VIP 給號
class VIPSeqn(models.Model):
  VIP_TYPE = (
      (1, "賭徒"),
      (2, "賭王"),
      (3, "賭霸"),
      (4, "賭聖"),
      (5, "賭俠"),
      (6, "賭神")
  )
  vip_type = models.PositiveIntegerField(_("VIP等級"), choices=VIP_TYPE, primary_key=True)
  vip_seqn = models.IntegerField(_("目前編號"),default=0)

# 新版組織圖
class VIPTree(models.Model):
  VIP_TYPE = (
      (0, ""),
      (1, "賭徒"),
      (2, "賭王"),
      (3, "賭霸"),
      (4, "賭聖"),
      (5, "賭俠"),
      (6, "賭神")
  )
  id = models.AutoField(_("id"),primary_key=True)
  vip_type = models.PositiveIntegerField(_("VIP等級"), choices=VIP_TYPE, default = 1)
  seat = models.PositiveIntegerField(_("Seat"), default = 0)
  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("玩家ID"))
  layer = models.PositiveIntegerField(_("Layer"), default = 0)
  parent = models.PositiveIntegerField(_("Parent"), default = 0)
  child1 = models.PositiveIntegerField(_("Child1"), default = 0)
  child2 = models.PositiveIntegerField(_("Child2"), default = 0)
  child3 = models.PositiveIntegerField(_("Child3"), default = 0)
  branch_count = models.PositiveIntegerField(_("分支數量"), default = 0)
  # 玩家加入此層級VIP時若其推薦人已加入則推薦人玩家ID才會填入
  bind_player = models.PositiveIntegerField(_("推薦人玩家ID"), default = 0)
  created_date = models.DateTimeField(auto_now_add=True)

  # 取得所有有效子節點
  def get_child_list(self):
    childlist = []
    if self.child1 > 0:
      childlist.append(self.child1)
    if self.child2 > 0:
      childlist.append(self.child2)
    if self.child3 > 0:
      childlist.append(self.child3)
    return childlist

  class Meta:
    indexes = [ 
      models.Index(fields=['vip_type','seat']), 
      ]

# 玩家後台系統專用 start --------------------------------------------------
# 玩家登入後台紀錄
class PlayerLoginInfo(models.Model):

  id = models.AutoField(_("ID"),primary_key=True)
  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("登入帳號ID"))
  login_date = models.DateTimeField(auto_now=True, verbose_name=_("登入時間"))
# 玩家後台系統專用 end ------------------------------------------------------

# 玩家出金紀錄
class PlayerOrder(models.Model):
  STATUS_TYPE = (
      ("1", "已出金"),
      ("2", "審核中")
  )
  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("玩家ID"))
  wallet_addr = models.CharField(_("錢包位址"),max_length=100, blank=True, default='')
  amount = models.PositiveIntegerField(_("鑽石"), default=0)
  created_date = models.DateTimeField(auto_now_add=True, verbose_name=_("日期"))
  status = models.CharField(_("狀態"),max_length=1, choices=STATUS_TYPE, default='2')
  old_amount = models.DecimalField(_("原始鑽石"), default=0,max_digits=20, decimal_places=4)
  done_user = models.CharField(_("出金確認者帳號"),max_length=20, default='')
  done_date = models.DateTimeField(_("出金確認時間"),blank=True,null=True)

# 獎金分配紀錄
class VIPBonus(models.Model):
  VIP_TYPE = (
      (1, "賭徒"),
      (2, "賭王"),
      (3, "賭霸"),
      (4, "賭聖"),
      (5, "賭俠"),
      (6, "賭神")
  )
  id = models.AutoField(_("id"),primary_key=True)
  vip_type = models.PositiveIntegerField(_("VIP等級"), choices=VIP_TYPE, default = 1)
  seat = models.PositiveIntegerField(_("Seat"), default = 0)
  player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=_("玩家ID"))
  level_player = models.PositiveIntegerField(_("見點獎金玩家ID"), default = 0)
  level_bouns = models.DecimalField(_("見點獎金"), default=0 ,max_digits=10, decimal_places=2)
  match_player = models.PositiveIntegerField(_("匹配獎金玩家ID"), default = 0)
  match_bonus = models.DecimalField(_("匹配獎金"), default=0 ,max_digits=10, decimal_places=2)
  created_date = models.DateTimeField(auto_now_add=True)

  class Meta:
    indexes = [ 
      models.Index(fields=['vip_type','seat','created_date']), 
      ]


# game server 玩家帳號資料
class user_view(models.Model):
  third_account = models.CharField(_("email"),max_length=128)
  password = models.CharField(_("密碼"),max_length=32)
  pid = models.CharField(_("UserId"),max_length=64,primary_key=True)

  class Meta(object):
    db_table='user_view'
    app_label = 'player_data'
        