# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import grequests

from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin

from datetime import datetime, timedelta
from django.db.models import Count, aggregates, Sum, Q, Max
#
from django.forms import ModelForm
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt

from rest_framework import generics, status, mixins, viewsets
from rest_framework.response import Response

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView

from gamecore.models import *
from gamecore.serializers import *

import uuid , calendar, requests
import decimal
import json
import logging

#from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse

logger1 = logging.getLogger('gamecore.views')

gameserver_headers = {
    "apiKey": "1qaz2WSX",
    "Content-Type": "application/json"
}
gameserver_url = 'http://65.52.184.150:12308/v1/gm/playerValue'

# Create your views here.
class Helpers():
    # OK
    def getIPHistory(self, player_id, ip_type, start_date, end_date):
        if start_date is not None and end_date is not None:
            result = IPInfo.objects.filter(player_id=player_id, type=ip_type, created_date__range=(start_date, end_date))
        if start_date is None and end_date is None:
            result = IPInfo.objects.filter(player_id=player_id, type=ip_type)
        return result

    # OK
    def getGameRoomList(self, room, start_date, end_date):
        if start_date is not None and end_date is not None:
            result = GameRoom.objects.filter(room=room, created_date__range=(start_date, end_date))
        if start_date is None and end_date is None:
            result = GameRoom.objects.filter(room=room)
        return result

    # OK
    def getGameRunList(self, game_room_id, start_date, end_date):
        if start_date is not None and end_date is not None:
            result = GameRoom.objects.filter(game_room_id=game_room_id, created_date__range=(start_date, end_date))
        if start_date is None and end_date is None:
            result = GameRoom.objects.filter(game_room_id=game_room_id)
        return result

    # ???????????????????????????
    def checkAgentPlayer(self, agent_id):
        counts = Player.objects.get(id=agent_id,permission_type='2').count()
        if counts == 0:
            return False

        return True
    
    # ????????????????????????
    def addChangePWDData(self, user_account, old_pwd, new_pwd , modify_user):
       # Insert data
        createdObj = ChangePWDLog.objects.create(
            user_account = user_account, 
            old_password = old_pwd,
            new_password = new_pwd, 
            modify_user = modify_user 
        )
        return createdObj

    # ??????????????????
    def addLoginData(self, user_id, login_system):
       # Insert data 
        createdObj = LoginInfo.objects.create(
            account_id_id = user_id, 
            login_system = login_system
        )
        return createdObj

    # ?????????????????????
    def get_admin_name(self, user_account):
        try:
            rs = Account.objects.get(user_account=user_account)
            return rs.user_name

        except Account.DoesNotExist:
            return ""
        
        return ""

    # ???????????????????????????
    def get_player_gold(self, player_id):
        try:
            rs = Player.objects.get(id=player_id)
            return rs.gold_total

        except Player.DoesNotExist:
            return 0
        
        return 0

    # ?????????????????????
    def get_player_nickname(self, player_id):
        try:
            rs = Player.objects.get(id=player_id)
            return rs.nick_name

        except Player.DoesNotExist:
            return ""
        
        return ""

    # ?????????????????????
    def get_admin_name(self, user_account):
        try:
            rs = Account.objects.get(user_account=user_account)
            return rs.user_name

        except Account.DoesNotExist:
            return ""
        
        return ""

    # ???????????????????????????
    def get_gamerun_area(self, run_id):
        try:
            rs = GameRun.objects.get(run_id=run_id)
            return rs.get_area_name()

        except GameRun.DoesNotExist:
            return ""
        
        return ""

    # ???????????????????????????
    def get_gamerun_state(self, run_id):
        try:
            rs = GameRun.objects.get(run_id=run_id)
            return rs.get_state_name()

        except GameRun.DoesNotExist:
            return ""
        
        return ""
                
    # ????????????????????????????????????
    def get_current_company_bonus(self):
      result = {}
      today = datetime.datetime.now()
      result['current_year'] = today.year
      result['current_month'] = today.month
      this_year_company_bonus = GoldFlow.objects.filter(type='5',created_date__year=today.year).aggregate(Sum('amount'))['amount__sum']
      if this_year_company_bonus is None:
          this_year_company_bonus = 0
      result['this_year_company_bonus'] = this_year_company_bonus
      this_month_company_bonus = GoldFlow.objects.filter(type='5',created_date__year=today.year,created_date__month=today.month).aggregate(Sum('amount'))['amount__sum']
      if this_month_company_bonus is None:
          this_month_company_bonus = 0
      result['this_month_company_bonus'] = this_month_company_bonus
      return result

    # ????????????????????????(by date)
    def get_company_bonus_by_month(self, search_month):
    #   print(f"[get_company_bonus_by_month]")
      result = []
      ls = search_month.split('/')
    #   print(f"[get_company_bonus_by_month]search_month:{search_month}")
      chk_year = int(ls[0])
      chk_month = int(ls[1])
    #   print(f"chk_year:{chk_year} chk_month:{chk_month}")
      monthRange = calendar.monthrange(chk_year, chk_month)[1]
    #   print(f"monthRange:{monthRange}")

      check_date = ""
      date_start = datetime.datetime(chk_year,chk_month,1,0,0,0,0)
      date_end = datetime.datetime(chk_year,chk_month,1,23,59,59,999999)
      
      for chk_day in range(0,monthRange,1):
        # print(f"[get_company_bonus_by_month]search_month:{search_month}")
        # print(f"[get_company_bonus_by_month]chk_date:{date_start} - {date_end}")
        rs = {}
        filters = Q()
        filters.children.append(("created_date__gte",date_start))
        filters.children.append(("created_date__lte",date_end))

        # ????????????
        bonus = GoldFlow.objects.filter(type='6'
                                       ).filter(filters
                                       ).aggregate(Sum('amount'))['amount__sum']

        if bonus is None:
          bonus = 0

        # print(f"search_month:{search_month}")
        # print(f"2:chk_month:{chk_month}")
        # ????????????
        game_count = GameRun.objects.filter(filters).count()
        if game_count is None:
          game_count = 0
        # print(f"search_month:{search_month}")
        # print(f"3:chk_month:{chk_month}")
        # ????????????
        online_count = IPInfo.objects.filter(type='1').filter(filters).count()

        if online_count is None:
          online_count = 0
        # print(f"search_month:{search_month}")
        # print(f"4:chk_month:{chk_month}")
        if not (bonus == 0 and game_count == 0 and online_count == 0):
          chk_date = datetime.datetime.strftime(date_start, "%Y-%m-%d")
        #   print(f"5:chk_date:{chk_date}")
          rs['chk_date'] =  chk_date
          rs['bonus'] = format(bonus, '0,.2f')
          rs['game_count'] = game_count
          rs['online_count'] = online_count
          rs['action'] = chk_date

          result.append(rs)

        date_start = date_start + timedelta(days=1)
        date_end = date_end + timedelta(days=1)

      return result

    # ????????????????????????(by date,hour)
    # ??????????????? YYYY-MM-DD
    def get_company_bonus_by_date(self, chk_date):
      result = []
      ls = chk_date.split('-')
    #   print(f"chk_date:{chk_date}")
      chk_year = int(ls[0])
      chk_month = int(ls[1])
      chk_day = int(ls[2])
      # print(f"chk_year:{chk_year} chk_month:{chk_month} chk_day:{chk_day}")
      date_start = datetime.datetime(chk_year,chk_month,chk_day,0,0,0,0)
      date_end = datetime.datetime(chk_year,chk_month,chk_day,0,59,59,999999)

      for chk_hour in range(0,24):
        # print(f"[get_company_bonus_by_date]chk_date:{date_start} - {date_end}")
        rs = {}
        filters = Q()
        filters.children.append(("created_date__gte",date_start))
        filters.children.append(("created_date__lte",date_end))

        # ????????????
        bonus = GoldFlow.objects.filter(type='6'
                                       ).filter(filters).aggregate(Sum('amount'))['amount__sum']

        if bonus is None:
          bonus = 0

        # ????????????
        online_count = IPInfo.objects.filter(type='1').filter(filters).count()

        if online_count is None:
          online_count = 0

        if not (bonus == 0 and online_count == 0):
          h1 = date_start.hour
          chk_hour = "{}:00 - {}:00".format('{:0>2d}'.format(h1), '{:0>2d}'.format(h1+1))
          rs['chk_hour'] =  chk_hour
          rs['bonus'] = format(bonus, '0,.2f')
          rs['online_count'] = online_count
        #   print(f"chk_hour:{chk_hour} bonus:{format(bonus, '0,.2f')} online_count:{online_count}")

          result.append(rs)
        
        date_start = date_start + timedelta(hours=1)
        date_end = date_end + timedelta(hours=1)

      return result
 
    # ???????????????ref name : ?????????id
    def get_player_ref_name(self, id):
        try:
            matchedPlayer = Player.objects.get(pk = id)
            # print(f"[get_player_ref_name]player_ref_name:{matchedPlayer.get_ref_name()}")
            return matchedPlayer.get_ref_name()

        except Player.DoesNotExist:
            # print("[get_player_ref_name]No player exist(id:{id})")
            return ""      
    
    # ?????????????????????????????????
    def get_player_total_score(self, id):
        # print(f"[get_player_total_score]player_id:{id}")
        # today = datetime.date.today()
        # print(f"[show_score]today:{today}")
        # yesterday = today -  timedelta(days=1)
        # print(f"[show_score]yesterday:{yesterday}")
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("player_id",id))
        # ???????????????
        count1 = PlayerRoundResult.objects.filter(q1).count()
        if count1 is None:
          count1 = 0

        # ????????????
        q2 = Q()
        q2.connector = "OR"
        q2.children.append(("win",1))
        q2.children.append(("win_self_hand",1))
        count2 = PlayerRoundResult.objects.filter(q1).filter(q2).count()
        if count2 is None:
          count2 = 0

        # ????????????
        q3 = Q()
        q3.connector = "AND"
        q3.children.append(("win_self_hand",1))
        count3 = PlayerRoundResult.objects.filter(q1).filter(q3).count()
        if count3 is None:
          count3 = 0

        # ????????????
        q4 = Q()
        q4.connector = "AND"
        q4.children.append(("win",id))
        count4 = PlayerRoundResult.objects.filter(q1).filter(q4).count()
        if count4 is None:
          count4 = 0

        # ????????????
        q5 = Q()
        q5.connector = "AND"
        q5.children.append(("lost_won",1))
        count5 = PlayerRoundResult.objects.filter(q1).filter(q5).count()
        if count5 is None:
          count5 = 0

        # ??????????????????
        count6 = PlayerGameRoom.objects.filter(q1).aggregate(Max('banker_count'))['banker_count__max']
        if count6 is None:
          count6 = 0

        # ???15????????????
        q7 = Q()
        q7.connector = "AND"
        q7.children.append(("base",15))
        count7 = PlayerRoundResult.objects.filter(q1).filter(q7).count()
        if count7 is None:
          count7 = 0

        # ???30????????????
        q8 = Q()
        q8.connector = "AND"
        q8.children.append(("base",30))
        count8 = PlayerRoundResult.objects.filter(q1).filter(q8).count()
        if count8 is None:
          count8 = 0

        rs = [count1, count2, count3, count4, count5, count6, count7, count8]
        return rs


    # ???????????????????????????(????????????????????????????????????????????????????????????)
    # ????????????(score_type)???
    # 1 : ????????????
    # 2 : ????????????
    # 3 : ????????????
    # 4 : ????????????
    # 5 : ????????????
    # 6 : ??????????????????
    # 7 : ???15????????????
    # 8 : ???30????????????
    def get_player_scores(self, id, score_type):
        # print(f"[get_player_total_score]player_id:{id}")

        now = datetime.datetime.now()
        #??????
        today = now
        today_start = today.replace(hour=0,minute=0,second=0,microsecond=0)
        today_end = today.replace(hour=23,minute=59,second=59,microsecond=999999)

        #??????
        yesterday = now - timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)
        yesterday_end = yesterday.replace(hour=23,minute=59,second=59,microsecond=999999)

        #??????????????????????????????(????????????????????????????????????????????????)
        this_week_start = now - timedelta(days=now.weekday())
        this_week_end = now + timedelta(days=6-now.weekday())
        this_week_start = this_week_start.replace(hour=0,minute=0,second=0,microsecond=0)
        this_week_end = this_week_end.replace(hour=23,minute=59,second=59,microsecond=999999)
        #??????????????????????????????
        last_week_start = now - timedelta(days=now.weekday()+7)
        last_week_end = now - timedelta(days=now.weekday()+1)
        last_week_start = last_week_start.replace(hour=0,minute=0,second=0,microsecond=0)
        last_week_end = last_week_end.replace(hour=23,minute=59,second=59,microsecond=999999)
        #??????????????????????????????
        this_month_start = datetime.datetime(now.year, now.month, 1)
        if now.month == 12:
            this_month_end = datetime.datetime(now.year+1, 1, 1) - timedelta(days=1)
        else:
            this_month_end = datetime.datetime(now.year, now.month + 1, 1) - timedelta(days=1)
            
        this_month_start = this_month_start.replace(hour=0,minute=0,second=0,microsecond=0)
        this_month_end = this_month_end.replace(hour=23,minute=59,second=59,microsecond=999999)
        #??????????????????????????????
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
        last_month_start = last_month_start.replace(hour=0,minute=0,second=0,microsecond=0)
        last_month_end = last_month_end.replace(hour=23,minute=59,second=59,microsecond=999999)

        score_type_name = ""
        total_count = 0         # ??????
        today_count = 0         # ??????
        yesterday_count = 0     # ??????
        this_week_count = 0     # ??????
        last_week_count = 0     # ??????
        this_month_count = 0    # ??????
        last_month_count = 0    # ??????

        day_count = ""
        week_count = ""
        month_count = ""

        filters = Q()
        filters.connector = "AND"
        filters.children.append(("player_id",id))

        # conn = Q()
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("created_date__gte",today_start))
        q1.children.append(("created_date__lte",today_end))

        q2 = Q()
        q2.connector = "AND"
        q2.children.append(("created_date__gte",yesterday_start))
        q2.children.append(("created_date__lte",yesterday_end))

        q3 = Q()
        q3.connector = "AND"
        q3.children.append(("created_date__gte",this_week_start))
        q3.children.append(("created_date__lte",this_week_end))

        q4 = Q()
        q4.connector = "AND"
        q4.children.append(("created_date__gte",last_week_start))
        q4.children.append(("created_date__lte",last_week_end))

        q5 = Q()
        q5.connector = "AND"
        q5.children.append(("created_date__gte",this_month_start))
        q5.children.append(("created_date__lte",this_month_end))

        q6 = Q()
        q6.connector = "AND"
        q6.children.append(("created_date__gte",last_month_start))
        q6.children.append(("created_date__lte",last_month_end))

        qtype = Q()
        if score_type == 2:   # ????????????
            qtype.connector = "OR"
        else:
            qtype.connector = "AND"

        if score_type == 2:   # ????????????
            qtype.children.append(("win",1))
            qtype.children.append(("win_self_hand",1))
        elif score_type == 3:   # ????????????
            qtype.children.append(("win_self_hand",1))
        elif score_type == 4:   # ????????????
            qtype.children.append(("win",id))
        elif score_type == 5:   # ????????????
            qtype.children.append(("lost_won",1))
        elif score_type == 7:   # ???15????????????
            qtype.children.append(("base",15))
        elif score_type == 8:   # ???30????????????
            qtype.children.append(("base",30))

        if score_type == 1:     # ????????????
            # ??????
            total_count = PlayerRoundResult.objects.filter(filters).count()
            if total_count is None:
                total_count = 0
            
            # ??????
            today_count = PlayerRoundResult.objects.filter(filters).filter(q1).count()
            if today_count is None:
                today_count = 0
            
            # ??????
            yesterday_count = PlayerRoundResult.objects.filter(filters).filter(q2).count()
            if yesterday_count is None:
                yesterday_count = 0

            # ??????
            this_week_count = PlayerRoundResult.objects.filter(filters).filter(q3).count()
            if this_week_count is None:
                this_week_count = 0

            # ??????
            last_week_count = PlayerRoundResult.objects.filter(filters).filter(q4).count()
            if last_week_count is None:
                last_week_count = 0

            # ??????
            this_month_count = PlayerRoundResult.objects.filter(filters).filter(q5).count()
            if this_month_count is None:
                this_month_count = 0

            # ??????
            last_month_count = PlayerRoundResult.objects.filter(filters).filter(q6).count()
            if last_month_count is None:
                last_month_count = 0

        elif score_type in (2, 3, 4, 5, 7, 8):
            # ??????
            total_count = PlayerRoundResult.objects.filter(filters).filter(qtype).count()
            if total_count is None:
                total_count = 0
            
            # ??????
            today_count = PlayerRoundResult.objects.filter(filters).filter(q1).filter(qtype).count()
            if today_count is None:
                today_count = 0
            
            # ??????
            yesterday_count = PlayerRoundResult.objects.filter(filters).filter(q2).filter(qtype).count()
            if yesterday_count is None:
                yesterday_count = 0

            # ??????
            this_week_count = PlayerRoundResult.objects.filter(filters).filter(q3).filter(qtype).count()
            if this_week_count is None:
                this_week_count = 0

            # ??????
            last_week_count = PlayerRoundResult.objects.filter(filters).filter(q4).filter(qtype).count()
            if last_week_count is None:
                last_week_count = 0

            # ??????
            this_month_count = PlayerRoundResult.objects.filter(filters).filter(q5).filter(qtype).count()
            if this_month_count is None:
                this_month_count = 0

            # ??????
            last_month_count = PlayerRoundResult.objects.filter(filters).filter(q6).filter(qtype).count()
            if last_month_count is None:
                last_month_count = 0
            
        elif score_type == 6:   # ??????????????????

            # ??????
            total_count = PlayerGameRoom.objects.filter(filters).aggregate(Max('banker_count'))['banker_count__max']
            if total_count is None:
                total_count = 0
            
            # ??????
            today_count = PlayerGameRoom.objects.filter(filters).filter(q1).aggregate(Max('banker_count'))['banker_count__max']
            if today_count is None:
                today_count = 0
            
            # ??????
            yesterday_count = PlayerGameRoom.objects.filter(filters).filter(q2).aggregate(Max('banker_count'))['banker_count__max']
            if yesterday_count is None:
                yesterday_count = 0

            # ??????
            this_week_count = PlayerGameRoom.objects.filter(filters).filter(q3).aggregate(Max('banker_count'))['banker_count__max']
            if this_week_count is None:
                this_week_count = 0

            # ??????
            last_week_count = PlayerGameRoom.objects.filter(filters).filter(q4).aggregate(Max('banker_count'))['banker_count__max']
            if last_week_count is None:
                last_week_count = 0

            # ??????
            this_month_count = PlayerGameRoom.objects.filter(filters).filter(q5).aggregate(Max('banker_count'))['banker_count__max']
            if this_month_count is None:
                this_month_count = 0

            # ??????
            last_month_count = PlayerGameRoom.objects.filter(filters).filter(q6).aggregate(Max('banker_count'))['banker_count__max']
            if last_month_count is None:
                last_month_count = 0

        if score_type == 1:   # ????????????
            score_type_name = "???????????????{}".format(total_count)
        elif score_type == 2:   # ????????????
            score_type_name = "???????????????{}".format(total_count)
        elif score_type == 3:   # ????????????
            score_type_name = "???????????????{}".format(total_count)
        elif score_type == 4:   # ????????????
            score_type_name = "???????????????{}".format(total_count)
        elif score_type == 5:   # ????????????
            score_type_name = "???????????????{}".format(total_count)
        elif score_type == 6:   # ??????????????????
            score_type_name = "?????????????????????{}".format(total_count)
        elif score_type == 7:   # ???15????????????
            score_type_name = "???15???????????????{}".format(total_count)
        elif score_type == 8:   # ???30????????????
            score_type_name = "???30???????????????{}".format(total_count)

        rs = {}
        rs['id'] = id
        rs['score_type'] = score_type_name
        rs['total_count'] = total_count
        rs['today_count'] = today_count
        rs['yesterday_count'] = yesterday_count
        rs['this_week_count'] = this_week_count
        rs['last_week_count'] = last_week_count
        rs['this_month_count'] = this_month_count
        rs['last_month_count'] = last_month_count
        # player_name = "??????ID???{} ????????????".format(player)
        day_count = "?????????{} <br>?????????{}".format(today_count,yesterday_count)
        week_count = "?????????{} <br>?????????{}".format(this_week_count,last_week_count)
        month_count = "?????????{} <br>?????????{}".format(this_month_count,last_month_count)
        rs['day_count'] = day_count
        rs['week_count'] = week_count
        rs['month_count'] = month_count
        return rs

    # call ???????????? API(?????????????????????)
    def call_client_api(self, player_id, gold):
        # print(f"[call_client_api]player_id:{player_id}, gold:{gold}")
        headers = {"apiKey": "1qaz2WSX"}
        # url = 'http://104.215.83.178:12308/v1/gm/playerGold'
        url = 'http://65.52.184.150:12308/v1/gm/playerGold'
        send_data = {'player_id': player_id,
                     'gold': gold}
        # call api (post)
        result = requests.post(url, data = send_data, headers = headers)
        # print(f"[call_client_api]result:{result}")
        # code : 0
        # message : Success

    # call ???????????? API(?????????????????????/???????????????)
    '''
        [request]
            player_id : ????????????
            mode : ???????????? 0:??????,1:?????? 
            amount : ?????????(???????????????)
        [response]
            code : ????????????, 0?????????,???0???????????????
            msg : ????????????
            error : ????????????
    '''

    def client_playerValue(self, player_id, mode, amount):
        # headers = {
        #     "apiKey": "1qaz2WSX",
        #     "Content-Type": "application/json"
        # }
        # url = 'http://104.215.83.178:12308/v1/gm/playerValue'
        # url = 'http://65.52.184.150:12308/v1/gm/playerValue'
        new_amount = int(amount)
        send_data = {
            "player_id": player_id,
            "mode":mode,
            "amount": new_amount
        }

        #================================================================
        d1=datetime.datetime.now()
        msg = "[client_playerValue]1-start"
        logger1.warning(msg)
        msg = f"[client_playerValue]send_data:{send_data}"
        logger1.warning(msg)
        #================================================================
        try:
            # call api (post)
            result = requests.post(gameserver_url, headers=gameserver_headers, data=json.dumps(send_data))
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[client_playerValue]done, spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
        except:
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[client_playerValue]exception, spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
        
        # code : 0
        # message : Success

    # ???????????????????????? ????????? GoldFlowSummary???
    def addGoldFlow(self, player_id, type, amount, admin_account):
        # ?????????????????????????????????????????????ID
        if type != '1' and player_id is None:
            return None
        
        total_amount = decimal.Decimal('0.0')
        available_amount = decimal.Decimal('0.0')
        flow_amount = decimal.Decimal('0.0')
        old_amount = decimal.Decimal('0.0')
        if GoldFlowSummary.objects.all().count() == 0:
            summary = GoldFlowSummary()
        else:
            summary = GoldFlowSummary.objects.get(pk=1)
            total_amount = summary.total_amount
            available_amount = summary.available_amount
            flow_amount = summary.flow_amount

        # ??????????????????????????????????????? GoldFlowSummary ??????
        if type == 1:  # ????????????
            old_amount = available_amount

        if player_id is not None:
            try:
                matchPlayer = Player.objects.get(pk=player_id)
                old_amount = matchPlayer.gold_total

            except Player.DoesNotExist:
                return None

        new_goldflow = GoldFlow()
        new_goldflow.type = type
        new_goldflow.amount = amount
        if player_id is not None:
            new_goldflow.target_player_id = player_id
            # ?????????????????????????????????????????? player ??? gold_total(??????)
            # 2 : ??????
            if type == '2':
                gold_total = matchPlayer.gold_total + amount
                matchPlayer.gold_total = gold_total
                # print(f"amount:{amount} new gold:{gold_total}")
                matchPlayer.last_modify_date = datetime.datetime.now()
                matchPlayer.save()

        new_goldflow.admin_account = admin_account
        new_goldflow.old_amount = old_amount
        new_goldflow.save()

        # ?????? GoldFlowSummary
        # ????????????
        if type == 1:
            total_amount += amount
            available_amount += amount
        else:
            available_amount += amount
            flow_amount -= flow_amount

        summary.total_amount = total_amount
        summary.available_amount = available_amount
        summary.flow_amount = flow_amount
        summary.last_modify_date = datetime.datetime.now()
        summary.save()

    def isPasswordCorrect(self, user_account, user_password):
        try:
            matched = Account.objects.get(user_account=user_account)
            ret_msg = ""
            # ????????????????????????
            if user_password != matched.user_password:
                ret_msg = "???????????????!!"

        except Account.DoesNotExist:
            ret_msg = "?????? {} ?????????".format(user_account)

        return ret_msg
    # ????????????????????????
    def isPlayerExist(self, player_id):
        ret_msg = ""
        if player_id is None:
            ret_msg = "[isPlayerExist]player_id is None !!"
            # print(ret_msg)
            return False
        if player_id == 0:
            ret_msg = "[isPlayerExist]player_id is invalid !!"
            # print(ret_msg)
            return False            
            
        # if not player_id.isdigit():
        #     ret_msg = "[isPlayerExist]player_id's format is not valid !!"
        #     print(ret_msg)
        #     return False              
        
        try:
            matched = Player.objects.get(pk=player_id)
            ret_msg = f"[isPlayerExist]player_id:{player_id} is exist !!"
            # print(ret_msg)
            return True

        except Player.DoesNotExist:
            ret_msg = f"[isPlayerExist]player_id:{player_id} is not exist !!"
            # print(ret_msg)

        return False
    # ??????????????????????????????
    def isAgentPlayerExist(self, player_id):
        ret_msg = ""
        if self.isPlayerExist(player_id) == True:
            try:
                matched = Player.objects.get(pk=player_id,permission_type="2")
                # print(f"[isAgentPlayerExist]player_id:{player_id} is exist !!")
                return True

            except Player.DoesNotExist:
                ret_msg = f"[isAgentPlayerExist]player_id:{player_id} is not a agent player !!"
                # print(ret_msg)
                return False
                
        return False

    # ??????????????????????????????
    def goldFlowProcess(self, player_id, goldtype, amount, admin_account):
        # ????????????????????????(GoldFlow) & GoldFlowSummary
        # ???????????????????????????
        if GoldFlowSummary.objects.all().count() == 0:
            summary = GoldFlowSummary.objects.create(
                total_amount = decimal.Decimal("0"), 
                available_amount = decimal.Decimal("0"),
                flow_amount = decimal.Decimal("0"),
                star = decimal.Decimal("0")
            )
        summary = GoldFlowSummary.objects.get(pk=1)
        # ?????????????????????????????????????????????
        total_amount = summary.total_amount
        # ???????????????
        available_amount = summary.available_amount
        # ???????????????
        flow_amount = summary.available_amount
        # ?????????????????? 1,6,7 ?????????????????????????????????????????????????????????
        # 1:????????????
        # 2:??????
        # 6:??????
        # 7:??????????????????
        # 8:??????????????????

        if goldtype not in ('1','6','7'):
            amount *= decimal.Decimal("-1")
        # ???????????????????????????
        newGoldFlow = GoldFlow.objects.create(
            target_player_id = player_id, 
            type = goldtype,
            amount = amount,
            admin_account = admin_account,
            old_amount = available_amount
        )
        # ?????? GoldFlowSummary
        available_amount += amount
        if goldtype == '1':
            total_amount += amount
        else:
            flow_amount -= amount
        
        summary.total_amount = total_amount
        summary.available_amount = available_amount
        summary.flow_amount = flow_amount
        summary.last_modify_date = datetime.datetime.now()
        summary.save()

    # ??????????????????????????? 0(???????????????????????????????????????)
    def getShowDigits(self, value):
        chk_str = str(value)
        # ???????????????????????????
        if chk_str.isdigit() == True:
            return value
        
        # ???????????????????????? 0
        v = decimal.Decimal(chk_str)
        if v == 0:
            return "0"
        else:
            return chk_str.rstrip('0')

    # ?????????5%??????
    def getAllBonus(self, value):
        all_bonus = decimal.Decimal('0')
        all_bonus = decimal.Decimal(value) * decimal.Decimal('0.05')
        if all_bonus < 10.0 and all_bonus > 0.0:
            all_bonus = decimal.Decimal('10.0')
        return all_bonus

    def procPlayerGameRoom(self, playerID, game_room_id, banker_count, score, start_gold, settle_gold,bonus):
        try:
            matched = PlayerGameRoom.objects.get(game_room_id=game_room_id, player_id = playerID)
            matched.banker_count += banker_count
            matched.score += score
            matched.settle_gold = settle_gold
            matched.bonus += bonus
            matched.last_modify_date = datetime.datetime.now()
            matched.save()
            
            obj = matched
        except:
            # Insert data 
            obj = PlayerGameRoom.objects.create(
                game_room_id = game_room_id, 
                player_id = playerID,
                banker_count = banker_count,
                score = score,
                start_gold = start_gold,
                settle_gold = settle_gold,
                commission = bonus,
                last_modify_date = datetime.datetime.now()
            )
        return obj

    # ????????????????????????????????????
    def procPlayerRoundResult(self, run_id):
        msg = '[procPlayerRoundResult]OK'
        try:
            matched = GameRun.objects.get(run_id = run_id)
            # Insert data
            # Player1
            win = 1 if matched.player1 == matched.win_player else 0
            lost_won = 1 if matched.player1 == matched.lost_won_player else 0
            win_self_hand = 1 if matched.player1 == matched.win_self_hand_player else 0
            banker = 1 if matched.player1 == matched.banker_player else 0
            obj1 = PlayerRoundResult.objects.create(
                game_run_id = matched.run_id, 
                player_id = matched.player1, 
                base = matched.base, 
                win = win,
                lost_won = lost_won,
                win_self_hand = win_self_hand,
                banker = banker,
                score = matched.player1_win, 
                start_gold = matched.player1_start_gold, 
                settle_gold = matched.player1_settle_gold, 
                corp_bonus = matched.player1_corp_bonus
            )

            # Player2
            win = 1 if matched.player2 == matched.win_player else 0
            lost_won = 1 if matched.player2 == matched.lost_won_player else 0
            win_self_hand = 1 if matched.player2 == matched.win_self_hand_player else 0
            banker = 1 if matched.player2 == matched.banker_player else 0
            obj3 = PlayerRoundResult.objects.create(
                game_run_id = matched.run_id, 
                player_id = matched.player2, 
                base = matched.base, 
                win = win,
                lost_won = lost_won,
                win_self_hand = win_self_hand,
                banker = banker,
                score = matched.player2_win, 
                start_gold = matched.player2_start_gold, 
                settle_gold = matched.player2_settle_gold, 
                corp_bonus = matched.player2_corp_bonus
            )

            # Player3
            win = 1 if matched.player3 == matched.win_player else 0
            lost_won = 1 if matched.player3 == matched.lost_won_player else 0
            win_self_hand = 1 if matched.player3 == matched.win_self_hand_player else 0
            banker = 1 if matched.player3 == matched.banker_player else 0
            obj3 = PlayerRoundResult.objects.create(
                game_run_id = matched.run_id, 
                player_id = matched.player3, 
                base = matched.base, 
                win = win,
                lost_won = lost_won,
                win_self_hand = win_self_hand,
                banker = banker,
                score = matched.player3_win, 
                start_gold = matched.player3_start_gold, 
                settle_gold = matched.player3_settle_gold, 
                corp_bonus = matched.player3_corp_bonus
            )

            # Player4
            win = 1 if matched.player4 == matched.win_player else 0
            lost_won = 1 if matched.player4 == matched.lost_won_player else 0
            win_self_hand = 1 if matched.player4 == matched.win_self_hand_player else 0
            banker = 1 if matched.player4 == matched.banker_player else 0
            obj4 = PlayerRoundResult.objects.create(
                game_run_id = matched.run_id, 
                player_id = matched.player4, 
                base = matched.base, 
                win = win,
                lost_won = lost_won,
                win_self_hand = win_self_hand,
                banker = banker,
                score = matched.player4_win, 
                start_gold = matched.player4_start_gold, 
                settle_gold = matched.player4_settle_gold, 
                corp_bonus = matched.player4_corp_bonus
            )
        except: 
            msg = '[procPlayerRoundResult]Error'

        return msg

    # ????????????????????????????????????????????????????????????????????????????????????
    def procPlayerGold(self, player_id, goldtype, settle_gold, amount):
        # print(f"[procPlayerGold]------------------------------")
        ret_msg = ""
        if decimal.Decimal(amount) != decimal.Decimal('0'):
            try:
                matched = Player.objects.get(pk = player_id)
                old_amount = matched.gold_total
                # ??????????????????
                newPlayerGold = PlayerGold.objects.create(
                    player_id = player_id, 
                    type = goldtype,
                    amount = decimal.Decimal(amount),
                    old_amount = old_amount
                )
                if goldtype == "5":    # ???????????????????????????????????????
                    matched.score += int(amount)
                # ?????????????????????
                matched.gold_total = decimal.Decimal(settle_gold)
                matched.last_modify_date = datetime.datetime.now()
                matched.save()
                # notify client
                self.client_playerValue(player_id,0,matched.gold_total)

            except Player.DoesNotExist:
                ret_msg = f"[procPlayerGold] Player({player_id} doesn't  exist ------------------------------"

            except :
                ret_msg = f"[procPlayerGold] error ------------------------------"

        else:
            ret_msg = "[procPlayerGold] The amount is 0"

    # ???????????????VIP????????????
    def getVIPName(self, player_id):
        ret_msg = ""
        vip_name = ""
        try:
            matched = Player.objects.get(pk = player_id)
            vip_name = matched.get_vip_type_display()

        except Player.DoesNotExist:
            ret_msg = f"[getVIPName] Player({player_id} doesn't  exist ------------------------------"
            # print(ret_msg)
        
        return vip_name

    # ??????VIP??????????????????????????????
    def transferGold(self, vip_type):
        # print(f"[transferGold]------------------------------")
        gold = decimal.Decimal('0')
        if vip_type == 1:
            gold = decimal.Decimal('30000')
        elif vip_type == 2:
            gold = decimal.Decimal('165000')
        elif vip_type == 3:
            gold = decimal.Decimal('350000')
        elif vip_type == 4:
            gold = decimal.Decimal('1600000')
        elif vip_type == 5:
            gold = decimal.Decimal('3500000')
        elif vip_type == 6:
            gold = decimal.Decimal('7000000')
        
        return gold

    # ??????VIP???????????????????????????
    def transferStar(self, vip_type):
        star = decimal.Decimal('0')
        if vip_type == 1:
            star = 10
        elif vip_type == 2:
            star = 50
        elif vip_type == 3:
            star = 100
        elif vip_type == 4:
            star = 500
        elif vip_type == 5:
            star = 1000
        elif vip_type == 6:
            star = 2000
        
        return star

    # ??????????????????
    def getNewSeat(self, vip_type):
        newSeat = 0
        try:
            matched = VIPSeqn.objects.get(vip_type = vip_type)
            newSeat = matched.vip_seqn + 1
            matched.vip_seqn = newSeat
            matched.save()

        except VIPSeqn.DoesNotExist:
            VIPSeqn.objects.create(
                vip_type = vip_type, 
                vip_seqn = 1
            )
            newSeat = 1

        return newSeat

    # ??????????????????
    # 1.???????????????????????????????????????????????????????????????????????????
    # 2.??????????????????????????????????????????????????????????????????????????????
    # 3.???2???????????????????????????????????????????????????????????????????????????
    def getRefSeat(self, vip_type, player_id):
        result = {}
        ref_seat = 0
        bind_player = 0
        isNewVip = True
        # ??????vip tree ???????????????
        vipcnt = VIPTree.objects.filter(vip_type = vip_type).count()
        if vipcnt > 0:
            matched = Player.objects.get(pk=player_id)
            ref_seat = matched.get_player_firstSeat(vip_type)
            # print(f"[getRefSeat]1.ref_seat:{ref_seat}, bind_player:{matched.bind_player}")
            # ????????????????????????????????????????????????
            if ref_seat > 0:
                bind_player = player_id
                isNewVip = False
            else: # ????????????????????????????????????????????????
                check_player = matched.bind_player
                while check_player > 0:  # ?????????????????????????????????????????????VIP
                    bind_matched = Player.objects.get(pk=check_player)
                    ref_seat = bind_matched.get_player_firstSeat(vip_type)
                    if ref_seat == 0:
                        check_player = bind_matched.bind_player
                    else:
                        bind_player = bind_matched.bind_player
                        break

                # print(f"[getRefSeat]2.ref_seat:{ref_seat}")
                if ref_seat > 0: # ??????????????????VIP
                    bind_player = matched.bind_player
                else: # ??????????????????VIP && ?????????????????????VIP?????????????????????????????????(1)
                    ref_seat = 1

                # print(f"[getRefSeat]3.ref_seat:{ref_seat}")

        result = {
            "isNewVip":isNewVip,
            "ref_seat": ref_seat,
            "bind_player":bind_player
        }
        # print(f"[getRefSeat]I -> vip_type:{vip_type}, player_id:{player_id}")
        # print(f"[getRefSeat]O -> isNewVip:{isNewVip}, ref_seat:{ref_seat}, bind_player:{bind_player}")

        return result
    # ??????????????????
    # ref_seat > 0 ????????? 
    def getParentSeat(self, vip_type, ref_seat):
        pSeat = 0
        if ref_seat > 0:
            chklist1 = []
            chklist1.append(ref_seat)
            pSeat = self.getObjectSeat(vip_type, 0, chklist1)

        # print(f"[getParentSeat]I -> vip_type:{vip_type}, ref_seat:{ref_seat}")
        # print(f"[getParentSeat]O -> parent:{pSeat}")

        return pSeat

    # ??????????????????
    def getObjectSeat(self, vip_type, checklayer, checklist):
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("vip_type",vip_type))
        q1.children.append(("seat__in",checklist))
        rs = VIPTree.objects.filter(q1).order_by('parent','seat')
        objSeat = 0
        step = 0
        if checklayer < 1:
            base = 0
        else:
            base = pow(3, checklayer - 1)
        
        tmp0 = []
        tmp1 = []
        tmp2 = []
        tmp3 = []
        # print(f"[getObjectSeat]I -> checklist:{checklist}, layer:{checklayer}, base:{base}")
        if checklayer < 1:
            data = rs[0]
            if data.branch_count == 0:
                tmp0.append(data.seat)
            elif data.branch_count == 1:
                tmp1.append(data.seat)
            elif data.branch_count == 2:
                tmp2.append(data.seat)
            elif data.branch_count == 3:
                tmp3.append(data.child1)
                tmp3.append(data.child2)
                tmp3.append(data.child3)

            if len(tmp0) > 0:
                objSeat = tmp0[0]
                return objSeat

            # print(f"[getObjectSeat]O2 -> tmp0:{tmp0}")
            # print(f"[getObjectSeat]O2 -> tmp1:{tmp1}")
            # print(f"[getObjectSeat]O2 -> tmp2:{tmp2}")
            # print(f"[getObjectSeat]O2 -> tmp3:{tmp3}")

            # ?????? tmp0 ???????????????
            if len(tmp1) > 0:
                objSeat = tmp1[0]
                return objSeat
            elif len(tmp2) > 0:
                objSeat = tmp2[0]
                return objSeat
            else:    # ??????????????????????????????????????????????????????????????????
                objSeat = self.getObjectSeat(vip_type, checklayer+1,tmp3)
                return objSeat
        else:
            for i in range(3):
                for j in range(base):
                    chkPos =  j * 3 + i
                    # print(f"[getObjectSeat]i:{i}, j:{j},step:{step}, chkPos:{chkPos}")
                    data = rs[chkPos]
                    # print(f"[getObjectSeat]i:{i}, j:{j}, seat:{data.seat}, branch_count:{data.branch_count}")
                    if data.branch_count == 0:
                        tmp0.append(data.seat)
                    elif data.branch_count == 1:
                        tmp1.append(data.seat)
                    elif data.branch_count == 2:
                        tmp2.append(data.seat)
                    elif data.branch_count == 3:
                        tmp3.append(data.child1)
                        tmp3.append(data.child2)
                        tmp3.append(data.child3)

                    # print(f"[getObjectSeat]O1 -> tmp0:{tmp0}")
                    # print(f"[getObjectSeat]O1 -> tmp1:{tmp1}")
                    # print(f"[getObjectSeat]O1 -> tmp2:{tmp2}")
                    # print(f"[getObjectSeat]O1 -> tmp3:{tmp3}")

                if len(tmp0) > 0:
                    objSeat = tmp0[0]
                    return objSeat            

            # print(f"[getObjectSeat]O2 -> tmp0:{tmp0}")
            # print(f"[getObjectSeat]O2 -> tmp1:{tmp1}")
            # print(f"[getObjectSeat]O2 -> tmp2:{tmp2}")
            # print(f"[getObjectSeat]O2 -> tmp3:{tmp3}")

            # ?????? tmp0 ???????????????
            if len(tmp1) > 0:
                objSeat = tmp1[0]
                return objSeat
            elif len(tmp2) > 0:
                objSeat = tmp2[0]
                return objSeat
            else:    # ??????????????????????????????????????????????????????????????????
                objSeat = self.getObjectSeat(vip_type, checklayer+1,tmp3)
                return objSeat

    # ???????????????
    #  1.??????????????????
    #  2.?????????????????? link ????????????????????????????????????
    #  3.????????????????????????????????????
    #    layer = ????????? + 1??????????????????????????????????????? 0
    def addNewSeat(self, vip_type, player_id, bind_player, pSeat):
        # ??????????????????
        newSeat = self.getNewSeat(vip_type)

        # ?????????????????????
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("vip_type",vip_type))
        q1.children.append(("seat",pSeat))
        parent = VIPTree.objects.get(q1)
        # ????????????layer
        newlayer = parent.layer + 1
        old_child1 = parent.child1
        old_child2 = parent.child2
        old_child3 = parent.child3
        if parent.child1 == 0:
            parent.child1 = newSeat
        elif parent.child2 == 0:
            parent.child2 = newSeat
        elif parent.child3 == 0:
            parent.child3 = newSeat

        parent.branch_count = parent.branch_count + 1
        parent.save()
        # print(f"[addNewSeat]------------------------------")
        # print(f"[addNewSeat]vip_type:{vip_type}, player_id:{player_id}")
        # print(f"[addNewSeat]bind_player:{bind_player}, newSeat:{newSeat}, pSeat:{pSeat}")
        # print(f"[addNewSeat]old_child1:{old_child1}, child1:{parent.child1}")
        # print(f"[addNewSeat]old_child2:{old_child2}, child2:{parent.child2}")
        # print(f"[addNewSeat]old_child3:{old_child3}, child3:{parent.child3}")

        # ???????????????
        newvip = VIPTree.objects.create(
            vip_type = vip_type,
            seat = newSeat,
            layer = newlayer,
            parent = pSeat,
            player_id = player_id,
            bind_player = bind_player
        )
        return newSeat

    # ??????????????????
    def modifyFirstSeat(self, vip_type, player_id, firstSeat):
        matched = Player.objects.get(id=player_id)
        if vip_type == 1:
            matched.vip1_seat = firstSeat
        elif vip_type == 2:
            matched.vip2_seat = firstSeat
        elif vip_type == 3:
            matched.vip3_seat = firstSeat
        elif vip_type == 4:
            matched.vip4_seat = firstSeat
        elif vip_type == 5:
            matched.vip5_seat = firstSeat
        elif vip_type == 6:
            matched.vip6_seat = firstSeat

        matched.save()

    # ????????????????????????
    def procCorpStar(self, player_id, starflow_type, star):
        # print(f"[procCorpStar]------------------------------")
        # print(f"[procCorpStar]player_id:{player_id},starflow_type:{starflow_type},star:{star} ")
        ret_msg = ""
        if decimal.Decimal(star) != decimal.Decimal('0'):
            old_star = decimal.Decimal('0.0')
            if GoldFlowSummary.objects.all().count() == 0:
                summary = GoldFlowSummary()
            else:
                summary = GoldFlowSummary.objects.get(pk=1)
                old_star = summary.star

            # print(f"[procCorpStar]1.starflow_type:{starflow_type}, old_star:{old_star}")
            # ????????????(2)???????????????(5)???????????????(6)?????????(8)?????????????????????????????????
            if starflow_type in ('2','5','6','8'):
                star *= decimal.Decimal("-1")
            # print(f"[procCorpStar]2.starflow_type:{starflow_type}, old_star:{old_star}")

            # ????????????????????????
            newCorpStar = StarFlow.objects.create(
                player_id = player_id, 
                starflow_type = starflow_type,
                old_star = old_star,
                star = star
            )
            # ???????????????????????????
            summary.star = summary.star + star
            summary.last_modify_date = datetime.datetime.now()
            summary.save()

            # print(f"[procCorpStar]OK. ")
        else:
            ret_msg = "[procCorpStar] The star is 0"
            # print(ret_msg)

    # ????????????????????????
    def procPlayerStar(self, player_id, obj_playerid, starflow_type, star):
        # print(f"[procPlayerStar]------------------------------")
        # print(f"[procPlayerStar]player_id:{player_id}, obj_playerid:{obj_playerid},starflow_type:{starflow_type},star:{star} ")
        error_msg = ""
        if star != 0:
            matched = Player.objects.get(pk = player_id)
            old_star = matched.star

            new_star = star
            # ??????????????????(1)???????????????(7)?????????????????????????????????
            if starflow_type in ('1','7'):
                new_star = star * -1

            try:
                # ????????????????????????
                obj = PlayerStar.objects.create(
                    player_id = player_id, 
                    star_type = starflow_type,
                    obj_playerid = obj_playerid,
                    old_star = old_star,
                    star = new_star
                )

                # ???????????????????????????
                # tmp = f"[procPlayerStar]player_id:{player_id}, old star:{matched.star} "
                # logger1.error(tmp)
                matched.star = matched.star + new_star
                matched.last_modify_date = datetime.datetime.now()
                matched.save()
                # tmp = f"[procPlayerStar]player_id:{player_id}, new star:{matched.star} "
                # logger1.error(tmp)
                # notify client
                if starflow_type not in ('5','6'): # ???????????????????????????????????????
                    self.client_playerValue(player_id,1,matched.star)
                
                # ??????????????????????????????
                if obj_playerid == 99999999:
                    self.procCorpStar(player_id, starflow_type, star)

                # ??????????????????????????????
                return matched.star
                # print(f"[procPlayerStar]OK. ")
            except :
                error_msg = f"[procPlayerStar] error ------------------------------"
                logger1.warning(error_msg)
                return 0
        else:
            error_msg = "[procPlayerStar] The star is 0"
            logger1.warning(error_msg)
            return 0

    # check player already in VIP or not
    def check_player_in_vip(self,vip_type, player_id):
        result = {}
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("vip_type",vip_type))
        q1.children.append(("player_id",player_id))

        rs1 = Player.objects.filter(q1).order_by("id")
        if rs1.count() > 0:
            result['isExist'] = True
            for d1 in rs1:
                result['id'] = d1.id
                result['seat'] = d1.seat_id
                # print(f"[check_player_in_vip]id:{d1.id},seat:{d1.seat_id} ")
                break
        else:
            result['isExist'] = False
        
        # print(f"[check_player_in_vip]result:{result}")
        return result

    # ??????????????????????????????
    def addPlayerLoginData(self, player_id):
       # Insert data 
        createdObj = PlayerLoginInfo.objects.create(
            player_id = player_id
        )
        return createdObj

    def get_playerinfo_bySeat(self, vip_type, seat):
        # print(f"[get_playerinfo_bySeat]vip_type:{vip_type}, seat:{seat}")
        result = {}
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("vip_type",vip_type))
        q1.children.append(("seat",seat))
        rs1 = VIPTree.objects.filter(q1)
        if rs1.count() > 0:
            result['isExist'] = True
            for d1 in rs1:
                result['player'] = d1.player_id
                result['nickname'] = self.get_player_ref_name(d1.player_id)
                break
        else:
            result['isExist'] = False

        return result        

    def getVIPResult(self, vip_type, player_id, check_seat):
        # print("[getVIPResult]")
        result = {}
        vip_type_count = 0
        fans_count = 0
        level10_count = 0
        member_count = 0
        top_seat = -1
        seat = -1
        pid_seat = -1

        if vip_type is None or vip_type == 0 or player_id is None or player_id == 0:
            # ?????????
            return result

        nickname = ''
        seat_player = 0
        data = []
        # ?????? check_seat ??????????????????????????? player_id ?????????VIP??????
        # ????????? player_id ????????????????????????????????? player_id ????????????
        if check_seat is not None and check_seat > 0:
            seat_result = self.get_playerinfo_bySeat(vip_type, check_seat)
            # print(f"[getVIPResult]seat_result:{seat_result}")
            if seat_result['isExist'] == True:
                seat_player = seat_result['player']
                nickname = seat_result['nickname']
                seat = check_seat
                # print(f"[getVIPResult]seat_player:{seat_player}, nickname:{nickname}")
            else:
                # ?????????
                return result
        else:
            # ?????????
            matched = Player.objects.get(id=player_id)
            nickname = matched.get_ref_name()
            orgin = matched.get_player_firstSeat(vip_type)
            # print(f"[getVIPResult]orgin:{orgin}")
            if orgin == 0:
                rs = {}
                rs['id'] = 0
                rs['pid'] = None
                rs['text'] = nickname + ' ????????????'
                rs['picurl'] = 'images.jpeg'
                rs['bind'] = 'N'
                children = {}
                rs['childrens'] = children
                data.append(rs)
                result = {"data":data,
                          "vip_type_count":vip_type_count,
                          "fans_count":fans_count,
                          "level10_count":level10_count,
                          "member_count":member_count,
                          "top_seat":top_seat,
                          "pid_seat":pid_seat}

                return result
            else:
                seat = orgin

        top_seat = seat
        seat1 = VIPTree.objects.get(seat = seat, vip_type = vip_type)
        pid_seat = seat1.parent
        rs = {}
        rs['id'] = seat
        rs['pid'] = None
        rs['text'] = nickname
        rs['picurl'] = 'images.jpeg'
        rs['bind'] = 'N'
        # ??????????????????node
        childlist1 = seat1.get_child_list()
        # print(f"[getVIPResult]childlist1:{childlist1}")
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("vip_type",vip_type))
        q1.children.append(("seat__in",childlist1))
        ret1 = VIPTree.objects.filter(q1).order_by("seat")
        children = []
        for d1 in ret1:
            newseat = d1.seat
            rs1 = {}
            rs1['id'] = d1.seat
            rs1['pid'] = d1.parent
            rs1['text'] = Helpers().get_player_ref_name(d1.player_id)
            rs1['picurl'] = 'images.jpeg'
            # ????????????????????????????????????????????????????????????????????????????????????
            if int(d1.bind_player) == int(player_id):
                rs1['bind'] = 'Y'
            else:
                rs1['bind'] = 'N'

            # ??????????????????node????????????node
            childlist2 = d1.get_child_list()
            # print(f"[getVIPResult]childlist2:{childlist2}")
            q2 = Q()
            q2.connector = "AND"
            q2.children.append(("vip_type",vip_type))
            q2.children.append(("seat__in",childlist2))
            ret2 = VIPTree.objects.filter(q2).order_by("seat")

            child = []
            for d2 in ret2:
                rs2 = {}
                rs2['id'] = d2.seat
                rs2['pid'] = d2.parent
                rs2['text'] = Helpers().get_player_ref_name(d2.player_id)
                rs2['picurl'] = 'images.jpeg'
                # ????????????????????????????????????????????????????????????????????????????????????
                if int(d2.bind_player) == int(player_id):
                    rs2['bind'] = 'Y'
                else:
                    rs2['bind'] = 'N'
            
                grandchild = []
                rs2['childrens'] = grandchild

                child.append(rs2)

            rs1['childrens'] = child
            children.append(rs1)
            # print(f"[getVIPResult]rs1:{rs1}")
            
        rs['childrens'] = children
        data.append(rs)

        vip_type_count = self.getVipCount(vip_type)
        fans_count = self.player_fans_count(player_id, vip_type)
        level10_count = self.player_fanslevel10_count(player_id, vip_type)
        member_count = self.player_member_count(player_id, vip_type)

        # print(f"[getVIPResult]fans_count:{fans_count}, level10_count:{level10_count}")
        # print(f"[getVIPResult]data:{data}")

        result = {"data":data,
                  "vip_type_count":vip_type_count,
                  "fans_count":fans_count,
                  "level10_count":level10_count,
                  "member_count":member_count,
                  "top_seat":top_seat,
                  "pid_seat":pid_seat}
        # print(f"[getVIPResult]result:{result}")
        # print(f"[getVIPResult]vip_type:{vip_type}, player_id:{player_id}")        
        # print(f"[getVIPResult]vip_type_count:{vip_type_count}, member_count:{member_count}")        
        # print(f"[getVIPResult]fans_count:{fans_count}, level10_count:{level10_count}")        
        return result
    
    # ??????????????????????????????????????????ID
    def get_player_bind_player(self, bindcode):
        bind_player = 0
        if bindcode is not None and len(bindcode) > 0 and bindcode != "0":
            # print(f"[helpers.get_player_bind_player]bindcode:{bindcode}")
            try:
                matched = Player.objects.get(linkcode=bindcode)
                bind_player = matched.id
            except Player.DoesNotExist:
                bind_player = 0
        return bind_player

    # ???????????????????????? VIP ??????
    def get_vip_type(self,amount):
        if amount == 10:
            return 1
        elif amount == 50:
            return 2
        elif amount == 100:
            return 3
        elif amount == 500:
            return 4
        elif amount == 1000:
            return 5
        elif amount == 2000:
            return 6
        else:
            return 0

    # ?????????????????????VIP
    def is_New_VIP(self, vip_type, player_id):
        isNewVip = True
        cnt = VIPTree.objects.filter(vip_type = vip_type,player_id=player_id).count()
        if cnt > 0:
            isNewVip = False

        return isNewVip

    # ?????????????????????????????????????????????
    def get_qual_bind_player(self, vip_type, player_id, seat):
        bind_player = 0
        try:
            matched = Player.objects.get(pk=player_id)
            bind_player = matched.bind_player
            if bind_player > 0:
                isNewVIP = self.is_New_VIP(vip_type,bind_player)
                if isNewVIP:
                    bind_player = 0
                else:
                    # ?????? bind_player ???????????????????????????????????????????????????????????????
                    bind_matched = Player.objects.get(pk=bind_player)
                    # print(f"[get_qual_bind_player]bind_player:{bind_player}")
                    check_seat = bind_matched.get_player_firstSeat(vip_type)
                    # print(f"[get_qual_bind_player]seat:{seat}, check_seat:{check_seat}")
                    if check_seat == seat:
                        bind_player = 0

        except Player.DoesNotExist:
            bind_player = 0
        
        return bind_player

    # ?????????????????????????????????(????????????????????????10???)
    def procStarBonus(self, player_id, vip_type, seat):
        d1=datetime.datetime.now()
        msg = f"[procStarBonus]1-start,para:player_id:{player_id}, vip_type:{vip_type}, seat:{seat}"
        logger1.warning(msg)
        # print(f"[procStarBonus]------------------------------")
        # print(f"[procStarBonus]player_id:{player_id}, vip_type:{vip_type}, seat:{seat}")
        # ?????????????????????????????????
        allstar = self.transferStar(vip_type)
        # ???????????? : ???????????? 5 %
        bonus1 = decimal.Decimal(allstar) * decimal.Decimal(0.05)
        # ???????????? : ??????????????? 50%
        bonus2 = bonus1 * decimal.Decimal(0.5)
        # ????????????????????????
        pSeat = VIPTree.objects.get(vip_type=vip_type,seat = seat)
        check_seat = pSeat.parent
        new_star = 0
        req_list = []
        # ???????????? 10 ???
        for i in range(10):
            pSeat = VIPTree.objects.get(vip_type=vip_type,seat = check_seat)
            check_seat = pSeat.parent
            # print(f"[procStarBonus]check_seat:{check_seat}")
            obj_player = pSeat.player_id
            # print(f"[procStarBonus]obj_player:{obj_player}")  
            # ??????????????????????????????
            # self.procPlayerStar(obj_player, player_id, "5", bonus1)
            new_star = self.procPlayerStar(obj_player, 99999999, "5", bonus1)
            send_data = {
              "player_id": obj_player,
              "mode":1,
              "amount": int(new_star)
            }
            req = grequests.request("POST",url=gameserver_url, data=json.dumps(send_data),headers=gameserver_headers)
            req_list.append(req)
            # ???????????????????????????????????????VIP??????????????????
            obj_bind_player = self.get_qual_bind_player(vip_type, obj_player, seat)
            # print(f"[procStarBonus]obj_bind_player:{obj_bind_player}")
            match_bonus = 0   # ????????????
            if obj_bind_player > 0:
              #self.procPlayerStar(obj_bind_player, player_id, "6", bonus2)
              new_star = self.procPlayerStar(obj_bind_player, 99999999, "6", bonus2)
              send_data = {
                "player_id": obj_bind_player,
                "mode":1,
                "amount": int(new_star)
              }
              req = grequests.request("POST",url=gameserver_url, data=json.dumps(send_data),headers=gameserver_headers)
              req_list.append(req)

              match_bonus = bonus2

            # ????????????????????????
            VIPBonus.objects.create(
                vip_type = vip_type,
                seat = seat,
                player_id = player_id, 
                level_player = obj_player,
                level_bouns = bonus1,
                match_player = obj_bind_player,
                match_bonus = match_bonus
            )

            if check_seat == 0: # ?????????????????????
                break

        if len(req_list) > 0:
          msg = f"[procStarBonus]2-req_list size:{len(req_list)}"
          logger1.warning(msg)
        
          resp = grequests.imap(req_list, grequests.Pool(5))

        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[procStarBonus]done, spent : {diff} seconds"
        logger1.warning(msg)
    # ???????????????VIP??????????????????
    def getVipCount(self, vip_type):
        vipcnt = VIPTree.objects.filter(vip_type = vip_type).count()
        if vipcnt is None:
            vipcnt = 0
        return vipcnt

    # ??????????????????
    # player_id:????????????ID
    # nick_name:??????
    # level_bouns:????????????
    # match_bonus:????????????
    def player_member_list(self, bind_player):
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("bind_player",bind_player))
        rs1 = Player.objects.filter(q1).values('id','nick_name','created_date')
        result = []
        if rs1.count() > 0:
            for d1 in rs1:
                rs = {}
                player_id = d1['id']
                rs['id'] = player_id
                rs['nick_name'] = d1['nick_name']
                rs['created_date'] = datetime.datetime.strftime(d1['created_date'], "%Y-%m-%d %H:%M:%S")
                level_bouns = self.get_bindplayer_levelbonus(player_id,bind_player)
                match_bonus = self.get_bindplayer_matchbonus(player_id,bind_player)
                rs['level_bouns'] = level_bouns
                rs['match_bonus'] = match_bonus
                # print(f"[player_member_list]bind_player:{bind_player}, player:{player_id}")
                # print(f"[player_member_list]level_bouns:{level_bouns}, match_bonus:{match_bonus}")
                result.append(rs)

        return result

    # ???????????????????????????????????????
    # player_id:??????ID
    # bind_player:????????????ID
    def get_bindplayer_levelbonus(self, player_id, bind_player):
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("player_id",player_id))
        q1.children.append(("level_player",bind_player))
        bonus = VIPBonus.objects.filter(q1).aggregate(Sum('level_bouns'))['level_bouns__sum']
        if bonus is None:
            bonus = "0"
        return bonus

    # ???????????????????????????????????????
    # player_id:??????ID
    # bind_player:????????????ID
    def get_bindplayer_matchbonus(self, player_id, bind_player):
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("level_player",player_id))
        q1.children.append(("match_player",bind_player))
        bonus = VIPBonus.objects.filter(q1).aggregate(Sum('match_bonus'))['match_bonus__sum']
        if bonus is None:
            bonus = "0"
        return bonus

    # ???????????????????????????list
    def player_fans_seatlist(self, player_id, vip_type):
        rslist = []
        # ??????VIP??????
        matched = Player.objects.get(pk=player_id)
        firstSeat = matched.get_player_firstSeat(vip_type)
        # firstSeat = 0 => ??????????????????VIP
        if firstSeat > 0:
            rslist.append(firstSeat)
            rslist = self.getSubTreeList(vip_type,firstSeat,rslist)

        # print(f"[player_fans_seatlist]rslist:{rslist}")
        return rslist

    # ?????????????????????????????????
    def player_fans_count(self, player_id, vip_type):
        cnt = 0
        rslist = self.player_fans_seatlist(player_id, vip_type)
        if len(rslist) > 0:
            # ??????list??????????????????????????????????????????
            cnt = len(rslist) - 1
        return cnt

    # ?????????????????????10?????????list
    def player_fanslevel10_list(self, player_id, vip_type):
        rslist = []
        # ??????VIP??????
        matched = Player.objects.get(pk=player_id)
        firstSeat = matched.get_player_firstSeat(vip_type)
        # firstSeat = 0 => ??????????????????VIP
        if firstSeat > 0:
            rslist.append(firstSeat)
            rslist = self.get10layerList(vip_type,firstSeat,rslist,0)

        # print(f"[player_fanslevel10_list]rslist:{rslist}")
        return rslist

    # ?????????????????????10???????????????
    def player_fanslevel10_count(self, player_id, vip_type):
        cnt = 0
        rslist = self.player_fanslevel10_list(player_id, vip_type)
        if len(rslist) > 0:
            # ??????list??????????????????????????????????????????
            cnt = len(rslist) - 1
        return cnt

    # ???????????????????????????????????????
    def player_member_count(self, player_id, vip_type):
        cnt = 0
        # ???????????????????????????list
        fanslist = self.player_fans_seatlist(player_id, vip_type)
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("vip_type",vip_type))
        q1.children.append(("seat__in",fanslist))
        rs1 = VIPTree.objects.filter(q1).values('player').distinct()
        fanslist = []
        for dd1 in rs1:
            fanslist.append(dd1['player'])

        # ??????????????????list??????player???????????????????????????
        q2 = Q()
        q2.connector = "AND"
        q2.children.append(("bind_player",player_id))
        q2.children.append(("id__in",fanslist))
        rs2 = Player.objects.filter(q2)
        cnt = rs2.count()

        return cnt

    # ??????????????????????????????????????????????????????
    # vip_type_count:?????????????????????
    # fans_count:?????????????????????
    # level10_count:10???????????????
    # member_count:???????????????
    def player_vip_summary(self, player_id, vip_type):
        vip_type_count = self.getVipCount(vip_type)
        fans_count = self.player_fans_count(player_id,vip_type)
        level10_count = self.player_fanslevel10_count(player_id,vip_type)
        member_count = self.player_member_count(player_id, vip_type)

        result = {
            "vip_type_count":vip_type_count,
            "fans_count":fans_count,
            "level10_count":level10_count,
            "member_count":member_count
        }

        return result

    # ???????????????????????????????????????list
    def getSubTreeList(self, vip_type, seat, rslist):
        q1 = Q()
        q1.connector = "AND"
        q1.children.append(("vip_type",vip_type))
        q1.children.append(("seat",seat))
        rs1 = VIPTree.objects.filter(q1)
        data = rs1[0]
        if data.branch_count > 0:
            if data.child1 > 0:
                rslist.append(data.child1)
                rslist = self.getSubTreeList(vip_type,data.child1,rslist)
            if data.child2 > 0:
                rslist.append(data.child2)
                rslist = self.getSubTreeList(vip_type,data.child2,rslist)
            if data.child3 > 0:
                rslist.append(data.child3)
                rslist = self.getSubTreeList(vip_type,data.child3,rslist)

        return rslist

    # ???????????????????????????????????????10??? list
    def get10layerList(self, vip_type, seat, rslist, layer):
        if layer <= 10:
            q1 = Q()
            q1.connector = "AND"
            q1.children.append(("vip_type",vip_type))
            q1.children.append(("seat",seat))
            rs1 = VIPTree.objects.filter(q1)
            data = rs1[0]
            if data.branch_count > 0:
                if data.child1 > 0:
                    rslist.append(data.child1)
                    rslist = self.get10layerList(vip_type,data.child1,rslist,layer+1)
                if data.child2 > 0:
                    rslist.append(data.child2)
                    rslist = self.get10layerList(vip_type,data.child2,rslist,layer+1)
                if data.child3 > 0:
                    rslist.append(data.child3)
                    rslist = self.get10layerList(vip_type,data.child3,rslist,layer+1)

        return rslist

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

# ?????????????????????(??????)
class AddPlayerView(APIView):
    serializer_class = PlayerSerializer
    #permission_classes = [AllowAny]
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = "[AddPlayerView(new_player)]1-start ===================="
        logger1.warning(msg)
        #================================================================
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[AddPlayerView(new_player)]2-serializer start,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            nickName = serializer.validated_data.get('nick_name')
            lineID = serializer.validated_data.get('line_id')
            mac_addr = serializer.validated_data.get('register_mac_addr')
            imei = serializer.validated_data.get('register_imei')
            bindcode = serializer.validated_data.get('bindcode')
            # Check existing account
            # ?????????????????????            
            #if Player.objects.filter(nick_name=nickName).count() != 0:
            #    return Response("Player '%s' already exist." % nickName, status=status.HTTP_400_BAD_REQUEST)
            # ??????line ID ???????????????
            if lineID is not None and len(lineID) > 0 and Player.objects.filter(line_id=lineID).count() != 0:
                #================================================================
                d3=datetime.datetime.now()
                diff = (d3 - d2).total_seconds()
                msg = f"[AddPlayerView(new_player)]2.1-Player line {lineID} already exist,spent : {diff} seconds"
                logger1.warning(msg)                
                #================================================================
                return Response("Player line '%s' already exist." % lineID, status=status.HTTP_400_BAD_REQUEST)
            # ?????? mac address & imei ????????????
            if mac_addr is None or len(mac_addr) == 0 :
                #================================================================
                d4=datetime.datetime.now()
                diff = (d4 - d2).total_seconds()
                msg = f"[AddPlayerView(new_player)]2.2-????????????MAC??????????????????!!,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================
                return Response("????????????MAC??????????????????!!", status=status.HTTP_400_BAD_REQUEST)
            if imei is None or len(imei) == 0:
                #================================================================
                d5=datetime.datetime.now()
                diff = (d5 - d2).total_seconds()
                msg = f"[AddPlayerView(new_player)]2.3-????????????IMEI????????????!!,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================
                return Response("????????????IMEI????????????!!", status=status.HTTP_400_BAD_REQUEST)
            
            #================================================================
            d6=datetime.datetime.now()
            diff = (d6 - d2).total_seconds()
            msg = f"[AddPlayerView(new_player)]3-serializer end,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            # save data into DB
            post_instance = serializer.save()
            #================================================================
            d7=datetime.datetime.now()
            diff = (d7 - d6).total_seconds()
            msg = f"[AddPlayerView(new_player)]3-serializer save end,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            # ????????????????????????????????????????????????ID??????
            if bindcode is not None and len(bindcode) > 0:
                post_instance.get_player_bind_player()
            
            #================================================================
            d8=datetime.datetime.now()
            diff = (d8 - d7).total_seconds()
            msg = f"[AddPlayerView(new_player)]4-get_bind_player,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            post_instance.last_modify_date = datetime.datetime.now()
            post_instance.save()

            serializer1 = UpdatePlayerSerializer(post_instance, context={'request': request})
            #================================================================
            d9=datetime.datetime.now()
            diff = (d9 - d8).total_seconds()
            msg = f"[AddPlayerView(new_player)]5-done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            return Response(serializer1.data)
        else:
        #================================================================
            d2_1=datetime.datetime.now()
            diff = (d2_1 - d1).total_seconds()
            msg = f"[AddPlayerView(new_player)]serializer has errors,spent : {diff} seconds"
            logger1.debug(msg)
        #================================================================
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlayerByNicknameDetailView(APIView):
    serializer_class = UpdatePlayerSerializer
    permission_classes = (IsAuthenticated,)
 
    def get(self, request, nick_name, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerByNicknameDetailView(playerbyname/{nick_name}]1-start ===================="
        logger1.warning(msg)
        #================================================================
        try:
            matchPlayer = Player.objects.get(nick_name=nick_name)
            serializer = PlayerSerializer(matchPlayer, context={'request': request})
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerByNicknameDetailView(playerbyname/{nick_name}]done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            return Response(serializer.data)
        except Player.DoesNotExist:
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerByNicknameDetailView(playerbyname/{nick_name}]Player {nick_name} does not exist,spent : {diff} seconds"
            logger1.debug(msg)
            #================================================================

            return Response("Player '%s' does not exist." % nick_name, status=status.HTTP_400_BAD_REQUEST)
  
class PlayerByLineDetailView(APIView):
    serializer_class = UpdatePlayerSerializer
    permission_classes = (IsAuthenticated,)
    error_msg = ""
    
    def get(self, request, line_id, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerByLineDetailView(playerbyline/{line_id}]1-start ===================="
        logger1.warning(msg)
        #================================================================
        try:
            matchPlayer = Player.objects.get(line_id=line_id)
            serializer = PlayerSerializer(matchPlayer, context={'request': request})
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerByLineDetailView(playerbyline/{line_id}]done, spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            return Response(serializer.data)
        except Player.DoesNotExist:
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerByLineDetailView(playerbyline/{line_id}]Line ID:{line_id} does not exist, spent : {diff} seconds"
            logger1.error(msg)
            #================================================================
            error_msg = f"[PlayerByLineDetailView(playerbyline/{line_id}]Line ID:{line_id} does not exist."
            return Response(error_msg , status=status.HTTP_400_BAD_REQUEST)
            
class PlayerDetailView(APIView):
    serializer_class = UpdatePlayerSerializer
    permission_classes = (IsAuthenticated,)
      
    def get(self, request, pk, format=None):
        msg = ""
        try:
            #================================================================
            d1=datetime.datetime.now()
            msg = f"[PlayerDetailView(player/{pk}]1-start(get) ===================="
            logger1.warning(msg)
            #================================================================
            matchPlayer = Player.objects.get(pk=pk)
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerDetailView(player/{pk}]2-get data from db,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            serializer = UpdatePlayerSerializer(matchPlayer, context={'request': request})
            #================================================================
            d3=datetime.datetime.now()
            diff = (d3 - d2).total_seconds()
            msg = f"[PlayerDetailView(player/{pk}]2-data serialize,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            return Response(serializer.data)
        except Player.DoesNotExist:
            #================================================================
            d4=datetime.datetime.now()
            diff = (d4 - d1).total_seconds()
            msg = f"[PlayerDetailView(player/{pk}]Player {pk} does not exist,spent : {diff} seconds"
            logger1.debug(msg)
            #================================================================

            return Response("Player '%s' does not exist." % pk, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        #================================================================
        d11=datetime.datetime.now()
        msg = f"[PlayerDetailView(player/{pk}]1-start(put) ===================="
        logger1.warning(msg)
        #================================================================

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            #================================================================
            d12=datetime.datetime.now()
            diff = (d12 - d11).total_seconds()
            msg = f"[PlayerDetailView(player/{pk}]2-serializer,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            nickName = serializer.validated_data.get('nick_name')
            line_id = serializer.validated_data.get('line_id')
            linePhoto = serializer.validated_data.get('line_profile_url')
            realName = serializer.validated_data.get('real_name')
            phone = serializer.validated_data.get('phone_number')
            permissionType = serializer.validated_data.get('permission_type')
            is_lock = serializer.validated_data.get('is_lock')
            gold_total = serializer.validated_data.get('gold_total')
            score = serializer.validated_data.get('score')
            email = serializer.validated_data.get('email')
            linkcode = serializer.validated_data.get('linkcode')
            bindcode = serializer.validated_data.get('bindcode')

            # Check existing account
            try:
                # Try to find the match player first
                matchedPlayer = Player.objects.get(pk=pk)
                #================================================================
                d13=datetime.datetime.now()
                diff = (d13 - d12).total_seconds()
                msg = f"[PlayerDetailView(player/{pk}]3.1-get data,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                if realName is not None and len(realName) > 0:
                    matchedPlayer.real_name = realName
                if phone is not None:
                    matchedPlayer.phone_number = phone
                if permissionType is not None and len(permissionType) > 0:
                    matchedPlayer.permission_type = permissionType
                if linePhoto is not None and len(linePhoto) > 0:
                    matchedPlayer.line_profile_url = linePhoto
                if nickName is not None:
                    matchedPlayer.nick_name = nickName
                if is_lock is not None:
                    matchedPlayer.is_lock = is_lock
                if gold_total is not None:
                    matchedPlayer.gold_total = gold_total
                if score is not None:
                    matchedPlayer.score = score
                if email is not None:
                    matchedPlayer.email = email
                if gold_total is not None:
                    matchedPlayer.gold_total = gold_total

                if linkcode is not None and len(linkcode) > 0:
                    matchedPlayer.linkcode = linkcode

                if bindcode is not None and len(bindcode) > 0:
                    matchedPlayer.bindcode = bindcode
                    matchedPlayer.get_player_bind_player()

                matchedPlayer.last_modify_date = datetime.datetime.now()
                matchedPlayer.save()
                #================================================================
                d14=datetime.datetime.now()
                diff = (d14 - d13).total_seconds()
                msg = f"[PlayerDetailView(player/{pk}]4.1-save data,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                new_matchedPlayer = Player.objects.get(pk=pk)
                serializer = UpdatePlayerSerializer(new_matchedPlayer, context={'request': request})
                #================================================================
                d15=datetime.datetime.now()
                diff = (d15 - d14).total_seconds()
                msg = f"[PlayerDetailView(player/{pk}]done,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================
                return Response(serializer.data)
            except Player.DoesNotExist:
                #================================================================
                d16=datetime.datetime.now()
                diff = (d16 - d12).total_seconds()
                msg = f"[PlayerDetailView(player/{pk}]Player {pk} does not exist,spent : {diff} seconds"
                logger1.debug(msg)
                #================================================================

                return Response("Player '%s' does not exist." % pk, status=status.HTTP_400_BAD_REQUEST)
        else:
            #================================================================
            d17=datetime.datetime.now()
            diff = (d17 - d11).total_seconds()
            msg = f"[PlayerDetailView(player/{pk}]serializer has error:{serializer.errors},spent : {diff} seconds"
            logger1.debug(msg)
            #================================================================
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddIPView(APIView):
    serializer_class = IPSerializer
    permission_classes = (IsAuthenticated,)
    error_msg = ""

    def post(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        error_msg = f"[AddIPView(new_ip)]1.start:{request.data} ==================="
        logger1.warning(error_msg)
        serializer = self.serializer_class(data=request.data)
        #================================================================
        if serializer.is_valid():
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[AddIPView(new_ip)]2-serializer valid,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            playerID = serializer.validated_data.get('player_id')
            ip_type = serializer.validated_data.get('type')
            mac_addr = serializer.validated_data.get('mac_addr')
            imei = serializer.validated_data.get('imei')
            # IP Type?????????(1)??? mac_addr
            # ?????? imei ?????????????????????
            if ip_type == '1':
                if mac_addr is None or len(mac_addr) == 0:
                    #================================================================
                    d3=datetime.datetime.now()
                    diff = (d3 - d1).total_seconds()
                    msg = f"[AddIPView(new_ip)]r1-??????ID {playerID} ??? mac ?????????????????????,spent : {diff} seconds"
                    logger1.debug(msg)
                    #================================================================

                    error_msg = f"[AddIPView(new_ip)]??????ID {playerID} ??? mac ?????????????????????"
                    return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
                # else:
                #     if imei is None or len(imei) == 0:
                #         error_msg = f"[AddIPView(new_ip)]??????ID {playerID} ??? imei ???????????????"
                #         logger1.error(error_msg)
                #         return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Find the match player first 
                matchPlayer = Player.objects.get(pk=playerID)
                serializer.save()
                #================================================================
                d4=datetime.datetime.now()
                diff = (d4 - d2).total_seconds()
                msg = f"[AddIPView(new_ip)]3-save data,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                # when login -> update match player last login datetime
                if ip_type == '1':
                    last_login_date = serializer.data.get('created_date')
                    matchPlayer.last_login_date = last_login_date
                    matchPlayer.save()

                #================================================================
                d5=datetime.datetime.now()
                diff = (d5 - d4).total_seconds()
                msg = f"[AddIPView(new_ip)]done,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================
                return Response(serializer.data)
            except Player.DoesNotExist:
                #================================================================
                d6=datetime.datetime.now()
                diff = (d6 - d2).total_seconds()
                msg = f"[AddIPView(new_ip)]Player {playerID} doesn't exist,spent : {diff} seconds"
                    
                logger1.debug(msg)
                #================================================================
                error_msg = f"[AddIPView(new_ip)]Player {playerID} doesn't exist."
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
        else:
            #================================================================
            d7=datetime.datetime.now()
            diff = (d7 - d1).total_seconds()
            msg = f"[AddIPView(new_ip)]serializer has error:{serializer.errors},spent : {diff} seconds"
            logger1.debug(msg)
            #================================================================

            error_msg = f"[AddIPView(new_ip)]serializer has error:{serializer.errors}"
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

class AllIPListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[AllIPListView(all_ipList)]1-start =============================="
        logger1.warning(msg)
        #================================================================

        queryset = IPInfo.objects.all().order_by('-created_date')

        serializer = IPSerializer(queryset, many=True, context={'request': request})

        if queryset.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[AllIPListView(all_ipList)]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

class AllIPListByTypeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, ip_type, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[AllIPListByTypeView(all_ipList/{ip_type})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        queryset = IPInfo.objects.filter(type=ip_type).order_by('-created_date')

        serializer = IPSerializer(queryset, many=True, context={'request': request})

        if queryset.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[AllIPListByTypeView(all_ipList/{ip_type})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

class IPListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, player_id, ip_type, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[IPListView(ipList/{player_id}/{ip_type})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        # Filter data based on input parameters
        result = IPInfo.objects.filter(player_id=player_id, type=ip_type)
        serializer = IPSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[IPListView(ipList/{player_id}/{ip_type})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

class IPListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, ip_type, start_date, end_date, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[IPListWithDateView(ipList/{player_id}/{ip_type}/{start_date}/{end_date})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
        # Filter data based on input parameters
        result = IPInfo.objects.filter(player_id=player_id, type=ip_type, created_date__range=(start_date1, end_date1))
        serializer = IPSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[IPListWithDateView(ipList/{player_id}/{ip_type}/{start_date}/{end_date})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

# ??????????????????
class AddValueView(APIView):
    serializer_class = AddValueSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = "[AddValueView(add_value)]1-start =============================="
        logger1.warning(msg)
        #================================================================

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            playerID = serializer.validated_data.get('player_id')
            type = serializer.validated_data.get('type')
            description = serializer.validated_data.get('description')
            admin_account = serializer.validated_data.get('admin_account')
            gold = serializer.validated_data.get('gold')

            try:
                # Find the match player first 
                matchPlayer = Player.objects.get(pk=playerID)
                if type == '2' and len(description) == 0: # ??????
                    return Response("???????????????????????????" , status=status.HTTP_400_BAD_REQUEST)
                
                if type == '8' and len(description) == 0: # ??????
                    return Response("?????????????????????" , status=status.HTTP_400_BAD_REQUEST)

                if len(admin_account) == 0:
                    return Response("???????????????????????????" , status=status.HTTP_400_BAD_REQUEST)

                post_instance = serializer.save()
                # ????????????????????????
                old_gold = matchPlayer.gold_total
                # ????????????????????????
                old_star = matchPlayer.star
                new_amount = 0
                if (type == '8'): # ???????????????????????????
                    post_instance.old_gold = old_star
                    post_instance.save()
                    # ????????????????????????(PlayerStar)
                    # obj_playerid = 99999999 (????????????)
                    newPlayerStar = PlayerStar.objects.create(
                        player_id = playerID,
                        obj_playerid = 99999999,
                        star_type = type,
                        star = gold,
                        old_star = old_star
                    )

                    newgold = decimal.Decimal(gold)
                    # ????????????????????????(GoldFlow) & GoldFlowSummary
                    Helpers().goldFlowProcess(playerID, type ,newgold,admin_account)
                    # ?????????????????????
                    matchPlayer.star += newgold
                    new_amount = matchPlayer.star
                else:
                    post_instance.old_gold = old_gold
                    post_instance.save()

                    # ????????????????????????(PlayerGold)
                    newPlayerGold = PlayerGold.objects.create(
                        player = playerID, 
                        type = type,
                        amount = gold,
                        old_amount = old_gold
                    )
                    newgold = decimal.Decimal(gold)
                    # ????????????????????????(GoldFlow) & GoldFlowSummary
                    Helpers().goldFlowProcess(playerID, type ,newgold,admin_account)
                    # ?????????????????????
                    matchPlayer.gold_total += newgold
                    new_amount = matchPlayer.gold_total

                matchPlayer.last_modify_date = datetime.datetime.now()
                matchPlayer.save()

                # notify client
                if (type == '8'): # ???????????????????????????
                    Helpers().client_playerValue(player_id,1,new_amount)
                else:
                    Helpers().client_playerValue(player_id,0,new_amount)

                #================================================================
                d2=datetime.datetime.now()
                diff = (d2 - d1).total_seconds()
                msg = f"[AddValueView(add_value)]2-done,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                return Response(serializer.data)
            except Player.DoesNotExist:
                return Response("Player '%s' does not exist." % playerID, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddValueListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, type, format=None):

        # Filter data based on input parameters
        result = AddValue.objects.filter(type=type)
        serializer = AddValueSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

class PlayerAddValueListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, type, format=None):

        # Filter data based on input parameters
        result = AddValue.objects.filter(player_id = player_id,type=type)
        serializer = AddValueSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

class PlayerAddValueListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, type, start_date, end_date, format=None):
        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")

        # Filter data based on input parameters
        result = AddValue.objects.filter(player_id = player_id, type=type, created_date__range=(start_date1, end_date1))
        serializer = AddValueSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

# ??????????????????
# ?????????????????????????????????(GoldFlowSummary)
class AddGoldFlowView(APIView):
    serializer_class = GoldFlowSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[AddGoldFlowView(gold_flow)]1-start =============================="
        logger1.warning(msg)
        #================================================================

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            playerID = serializer.validated_data.get('target_player_id')
            admin_account = serializer.validated_data.get('admin_account')
            
            # ?????????????????????????????????????????????ID
            if type != '1' and playerID is None:
                return Response("???????????????ID???" , status=status.HTTP_400_BAD_REQUEST)

            try:
                # Find the match player first 
                matchPlayer = Player.objects.get(id=playerID)
                old_amount = matchPlayer.gold_total

                post_instance = serializer.save()
                # ????????????????????????
                old_gold = matchPlayer.gold_total
                post_instance.old_amount = old_gold
                post_instance.save()
                # ?????????????????????????????????????????? player ??? gold_total(??????)
                # 2 : ?????? , 3 : ???????????????
                if type == '2' or type == '3':
                    amount = serializer.validated_data.get('amount')
                    # print(f"old gold:{matchPlayer.gold_total}")
                    gold_total = matchPlayer.gold_total + amount
                    matchPlayer.gold_total = gold_total
                    # print(f"amount:{amount} new gold:{gold_total}")
                    matchPlayer.last_modify_date = datetime.datetime.now()
                    matchPlayer.save()

                #================================================================
                d2=datetime.datetime.now()
                diff = (d2 - d1).total_seconds()
                msg = f"[AddGoldFlowView(gold_flow)]2-done,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                return Response(serializer.data)
            except Player.DoesNotExist:
                return Response("Player '%s' does not exist." % playerID, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoldFlowListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, type,format=None):

        result = GoldFlow.objects.filter(type=type)
        serializer = GoldFlowSerializer(result, many=True, context={'request': request})
        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

class GoldFlowListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, type, start_date, end_date, format=None):
        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")

        result = GoldFlow.objects.filter(type=type, created_date__range=(start_date1, end_date1))
        serializer = GoldFlowSerializer(result, many=True, context={'request': request})
        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

# ??????????????????(GoldFlowSummary)
class GoldFlowSummaryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        result = GoldFlowSummary.objects.all()
        serializer = GoldFlowSummarySerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

# ??????????????????
class AddPlayerTransferView(APIView):
    serializer_class = PlayerTransferSerializer
    permission_classes = (IsAuthenticated,)

    error_msg = ""
    def post(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[AddPlayerTransferView(player_transfer)]1-start =========================="
        logger1.warning(msg)
        #================================================================
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[AddPlayerTransferView(player_transfer)]2-serializer,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            sender_id = serializer.validated_data.get('sender_id')
            amount = serializer.validated_data.get('amount')
            # jewel_type:1 -> ?????? 
            # jewel_type:2 -> ??????
            jewel_type = serializer.validated_data.get('jewel_type')
            jewel_desc = '??????'
            if jewel_type == 2:
                jewel_desc = '??????'

            try:
                # Find the match player first 
                matchPlayer1 = Player.objects.get(id=sender_id)
                if jewel_type == 2:
                    old_gold1 = matchPlayer1.star
                else:
                    old_gold1 = matchPlayer1.gold_total

                retMsg = f"????????? {sender_id} ?????????{jewel_desc}???"
                if old_gold1 < amount:
                    #================================================================
                    d3=datetime.datetime.now()
                    diff = (d3 - d2).total_seconds()
                    msg = f"[AddPlayerTransferView(player_transfer)]r1-{retMsg},spent : {diff} seconds"
                    logger1.warning(msg)
                    #================================================================
                    return Response(retMsg, status=status.HTTP_400_BAD_REQUEST)

            except Player.DoesNotExist:
                #================================================================
                d4=datetime.datetime.now()
                diff = (d4 - d2).total_seconds()
                msg = f"[AddPlayerTransferView(player_transfer)]Sender {sender_id} does not exist,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================
                error_msg = f"[AddPlayerTransferView(player_transfer)]Sender {sender_id} does not exist."
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

            receiver_id = serializer.validated_data.get('receiver_id')

            d5=datetime.datetime.now()
            try:
                # Find the match player first 
                matchPlayer2 = Player.objects.get(id=receiver_id)
                if jewel_type == 2:
                    old_gold2 = matchPlayer2.star
                else:
                    old_gold2 = matchPlayer2.gold_total

                post_instance = serializer.save()
                post_instance.sender_gold = int(old_gold1)
                post_instance.receiver_gold = int(old_gold2)
                post_instance.save()
                #================================================================
                d6=datetime.datetime.now()
                diff = (d6 - d5).total_seconds()
                msg = f"[AddPlayerTransferView(player_transfer)]post_instance save,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                player1_amount = 0
                player2_amount = 0
                # ????????????????????????
                if jewel_type == 2:
                    matchPlayer1.star -= amount
                    matchPlayer2.star += amount
                    player1_amount = matchPlayer1.star
                    player2_amount = matchPlayer2.star
                else:
                    matchPlayer1.gold_total -= amount
                    matchPlayer2.gold_total += amount
                    player1_amount = matchPlayer1.gold_total
                    player2_amount = matchPlayer2.gold_total

                matchPlayer1.last_modify_date = datetime.datetime.now()
                matchPlayer1.save()
                matchPlayer2.last_modify_date = datetime.datetime.now()
                matchPlayer2.save()
                #================================================================
                d7=datetime.datetime.now()
                diff = (d7 - d6).total_seconds()
                msg = f"[AddPlayerTransferView(player_transfer)]????????????????????????,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                if jewel_type == 2:
                    # ??????????????????????????????
                    startype = "3"
                    amount1 = amount * -1.0
                    newPlayerStar1 = PlayerStar.objects.create(
                        player_id = sender_id, 
                        star_type = startype,
                        obj_playerid = receiver_id,
                        star = amount1,
                        old_star = old_gold1
                    )

                    # ??????????????????????????????
                    startype = "4"
                    newPlayerStar2 = PlayerStar.objects.create(
                        player_id = receiver_id, 
                        star_type = startype,
                        obj_playerid = sender_id,
                        star = amount,
                        old_star = old_gold2
                    )
                    #================================================================
                    d8=datetime.datetime.now()
                    diff = (d8 - d7).total_seconds()
                    msg = f"[AddPlayerTransferView(player_transfer)]????????????????????????,spent : {diff} seconds"
                    logger1.warning(msg)
                    #================================================================

                    # notify client
                    Helpers().client_playerValue(sender_id,1,player1_amount)
                    Helpers().client_playerValue(receiver_id,1,player2_amount)
                    #================================================================
                    d9=datetime.datetime.now()
                    diff = (d9 - d8).total_seconds()
                    msg = f"[AddPlayerTransferView(player_transfer)]notify client,spent : {diff} seconds"
                    logger1.warning(msg)
                    #================================================================
                else:
                    # ????????????????????????
                    goldtype = "3"
                    amount1 = amount * -1.0
                    newPlayerGold1 = PlayerGold.objects.create(
                        player_id = sender_id, 
                        type = goldtype,
                        amount = amount1,
                        old_amount = old_gold1
                    )
                    # ????????????????????????
                    goldtype = "4"
                    newPlayerGold2 = PlayerGold.objects.create(
                        player_id = receiver_id, 
                        type = goldtype,
                        amount = amount,
                        old_amount = old_gold2
                    )
                    #================================================================
                    d8_1=datetime.datetime.now()
                    diff = (d8_1 - d7).total_seconds()
                    msg = f"[AddPlayerTransferView(player_transfer)]??????????????????,spent : {diff} seconds"
                    logger1.warning(msg)
                    #================================================================
                    # notify client
                    Helpers().client_playerValue(sender_id,0,player1_amount)
                    Helpers().client_playerValue(receiver_id,0,player2_amount)
                    #================================================================
                    d9_1=datetime.datetime.now()
                    diff = (d9_1 - d8_1).total_seconds()
                    msg = f"[AddPlayerTransferView(player_transfer)]notify client,spent : {diff} seconds"
                    logger1.warning(msg)
                    #================================================================

                return Response(serializer.data)
            except Player.DoesNotExist:
                error_msg = f"[AddPlayerTransferView(player_transfer)]Receiver {recevier_id} does not exist."
                logger1.debug(error_msg)                
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
        else:
            #================================================================
            d10=datetime.datetime.now()
            diff = (d10 - d1).total_seconds()
            msg = f"[AddPlayerTransferView(player_transfer)]serializer.error: {serializer.errors},spent : {diff} seconds"
            logger1.debug(msg)
            #================================================================
            error_msg = f"[AddPlayerTransferView(player_transfer)]serializer.error: {serializer.errors}"
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

class SenderTransferListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, jewel_type, format=None ):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[SenderTransferListView(sender_transfer/{player_id}/{jewel_type})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        # Filter data based on input parameters
        result = TransferGold.objects.filter(sender_id=player_id, jewel_type=jewel_type)
        serializer = PlayerTransferListSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[SenderTransferListView(sender_transfer/{player_id}/{jewel_type})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================        
        return Response(serializer.data)

class ReceiverTransferListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, jewel_type, format=None ):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[ReceiverTransferListView(receiver_transfer/{player_id}/{jewel_type})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        # Filter data based on input parameters
        result = TransferGold.objects.filter(receiver_id=player_id, jewel_type=jewel_type)
        serializer = PlayerTransferListSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)
        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[ReceiverTransferListView(receiver_transfer/{player_id}/{jewel_type})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================        
        return Response(serializer.data)
  
class SenderTransferListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, start_date, end_date, jewel_type, format=None ):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[SenderTransferListWithDateView](sender_transfer/{player_id}/{start_date}/{end_date}/{jewel_type})1-start ============================="
        logger1.warning(msg)
        #================================================================
        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")

        # Filter data based on input parameters
        result = TransferGold.objects.filter(sender_id=player_id, jewel_type=jewel_type, 
                                             created_date__range=(start_date1, end_date1))
        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[SenderTransferListWithDateView]2-filter,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        serializer = PlayerTransferListSerializer(result, many=True, context={'request': request})
        
        #================================================================
        d3=datetime.datetime.now()
        diff = (d3 - d2).total_seconds()
        msg = f"[SenderTransferListWithDateView]3-serializer,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

class ReceiverTransferListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, start_date, end_date, jewel_type, format=None ):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[ReceiverTransferListWithDateView](receiver_transfer/{player_id}/{start_date}/{end_date}/{jewel_type})1-start ============================="
        logger1.warning(msg)
        #================================================================

        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")

        # Filter data based on input parameters
        result = TransferGold.objects.filter(receiver_id=player_id,  jewel_type=jewel_type, 
                                             created_date__range=(start_date1, end_date1))
        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[ReceiverTransferListWithDateView]2-filter,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        serializer = PlayerTransferListSerializer(result, many=True, context={'request': request})

        #================================================================
        d3=datetime.datetime.now()
        diff = (d3 - d2).total_seconds()
        msg = f"[ReceiverTransferListWithDateView]3-serializer,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

# ??????????????????
class AddPlayerGoldView(APIView):
    serializer_class = PlayerGoldSerializer
    permission_classes = (IsAuthenticated,)
    error_msg = ""
    def post(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[AddPlayerGoldView(player_gold)]1-start =============================="
        logger1.warning(msg)
        #================================================================
                
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            player_id = serializer.validated_data.get('player_id')
            #================================================================
            msg = f"[AddPlayerGoldView(player_gold)]2-player_id:{player_id} =============================="
            logger1.warning(msg)
            #================================================================

            try:
                # Find the match player first 
                matchPlayer = Player.objects.get(id=player_id)

                post_instance = serializer.save()
                # ????????????????????????
                old_gold = matchPlayer.gold_total
                post_instance.old_amount = old_gold
                post_instance.save()

                action_type = serializer.validated_data.get('type')
                check_type = ['3', '4']
                if action_type in check_type :
                    # ????????????????????? player ??? gold_total(??????)
                    amount = serializer.validated_data.get('amount')
                    # 4:?????? ==> ????????????
                    if action_type == '4':
                        gold_total = matchPlayer.gold_total + amount
                    # 3:?????? ==> ????????????
                    elif action_type == '3':
                        gold_total = matchPlayer.gold_total - amount
                    # print(f"type:{action_type}, old gold:{matchPlayer.gold_total}")
                    # print(f"amount:{amount} new gold:{gold_total}")
                    matchPlayer.gold_total = gold_total
                    matchPlayer.last_modify_date = datetime.datetime.now()
                    matchPlayer.save()
                    # notify client
                    Helpers().client_playerValue(player_id,0,matchPlayer.gold_total)

                #================================================================
                d2=datetime.datetime.now()
                diff = (d2 - d1).total_seconds()
                msg = f"[AddPlayerGoldView(player_gold)]2-done,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================
                return Response(serializer.data)
            except Player.DoesNotExist:
                #================================================================
                error_msg = f"[AddPlayerGoldView]Player {player_id} does not exist." 
                logger1.debug(error_msg)
                #================================================================
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
        else:
            #================================================================
            error_msg = f"[AddPlayerGoldView]serializer has error:{serializer.errors}"
            logger1.error(error_msg)
            #================================================================
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlayerGoldListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, type, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerGoldListView(player_gold_Listbytype/{player_id}/{type})]1-start =============================="
        logger1.warning(msg)
        #================================================================
        
        # Filter data based on input parameters
        result = PlayerGold.objects.filter(player_id=player_id, type = type)
        serializer = PlayerGoldSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[PlayerGoldListView(player_gold_Listbytype/{player_id}/{type})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

class PlayerGoldListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, type, start_date, end_date, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerGoldListWithDateView(player_gold_Listbytype)]1-start =============================="
        logger1.warning(msg)
        #================================================================

        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
        
        # Filter data based on input parameters
        result = PlayerGold.objects.filter(player_id=player_id, type = type, created_date__range=(start_date1, end_date1))
        serializer = PlayerGoldSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[PlayerGoldListWithDateView(player_gold_Listbytype/{player_id}/{type}/{start_date}/{end_date})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

# ????????????
class AddGameRoomView(APIView):
    serializer_class = GameRoomSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[AddGameRoomView(game_room)]1-start =============================="
        logger1.warning(msg)
        #================================================================
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            post_instance = serializer.save()
            datetime1 = post_instance.created_date
            post_instance.last_modify_date = datetime1
            post_instance.save()

            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[AddGameRoomView(game_room)]2-done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GameRoomDetailView(APIView):
    serializer_class = GameRoomDetailSerializer
    permission_classes = (IsAuthenticated,)
      
    def get(self, request, pk, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[GameRoomDetailView(game_room/{pk})-get]1-start =============================="
        logger1.warning(msg)
        #================================================================

        try:
            matchGameRoom = GameRoom.objects.get(pk=pk)
            serializer = GameRoomDetailSerializer(matchGameRoom, context={'request': request})

            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[GameRoomDetailView(game_room/{pk})-get]2-done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            
            return Response(serializer.data)

        except GameRoom.DoesNotExist:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[GameRoomDetailView(game_room/{pk})-put]1-start =============================="
        logger1.warning(msg)
        #================================================================

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            room = serializer.validated_data.get('room')
            room_create_date = serializer.validated_data.get('room_create_date')
            state = serializer.validated_data.get('state')
            start_date = serializer.validated_data.get('start_date')
            total_commission = serializer.validated_data.get('total_commission')

            # Check existing account
            try:
                # Try to find the match player first
                matchGameRoom = GameRoom.objects.get(pk=pk)
                matchGameRoom.room = room
                matchGameRoom.room_create_date = room_create_date
                matchGameRoom.state = state
                matchGameRoom.start_date = start_date
                matchGameRoom.total_commission = total_commission
                matchGameRoom.last_modify_date = datetime.datetime.now()
                matchGameRoom.save()

                serializer = GameRoomDetailSerializer(matchGameRoom, context={'request': request})

                #================================================================
                d2=datetime.datetime.now()
                diff = (d2 - d1).total_seconds()
                msg = f"[GameRoomDetailView(game_room/{pk})-put]2-done,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================
            
                return Response(serializer.data)
            except GameRoom.DoesNotExist:
                return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GameRoomListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, room, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[GameRoomListView(game_room_List/{room})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        # Filter data based on input parameters
        result = GameRoom.objects.filter(room=room)
        serializer = GameRoomDetailSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[GameRoomListView(game_room_List/{room})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================
 
        return Response(serializer.data)

class GameRoomListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, room, start_date, end_date, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[GameRoomListWithDateView(game_room_List/{room}/{start_date}/{end_date})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")

        # Filter data based on input parameters
        result = GameRoom.objects.filter(room=room, created_date__range=(start_date1, end_date1))
        serializer = GameRoomDetailSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[GameRoomListWithDateView(game_room_List/{room}/{start_date}/{end_date})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

# ????????????
class AddGameRunView(APIView):
    serializer_class = GameRunSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[AddGameRunView(game_run)]1-start =============================="
        logger1.warning(msg)
        #================================================================

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            run_id = serializer.validated_data.get('run_id')
            game_room_id = serializer.validated_data.get('game_room_id')
            player1 = serializer.validated_data.get('player1')
            player2 = serializer.validated_data.get('player2')
            player3 = serializer.validated_data.get('player3')
            player4 = serializer.validated_data.get('player4')
            win_player = serializer.validated_data.get('win_player')
            if win_player is None:
                win_player = 0
            
            lost_won_player = serializer.validated_data.get('lost_won_player')
            if lost_won_player is None:
                lost_won_player = 0

            win_self_hand_player = serializer.validated_data.get('win_self_hand_player')
            if win_self_hand_player is None:
                win_self_hand_player = 0

            banker_player = serializer.validated_data.get('banker_player')
            if banker_player is None:
                banker_player = 0

            player1_win = serializer.validated_data.get('player1_win')
            if player1_win is None:
                player1_win = 0

            player2_win = serializer.validated_data.get('player2_win')
            if player2_win is None:
                player2_win = 0

            player3_win = serializer.validated_data.get('player3_win')
            if player3_win is None:
                player3_win = 0

            player4_win = serializer.validated_data.get('player4_win')
            if player4_win is None:
                player4_win = 0

            # player1
            try:
                matched1 = Player.objects.get(pk=player1)
                old_gold1 = matched1.gold_total
                old_score1 = matched1.score

            except Player.DoesNotExist:
                return Response("Player1 '%s' does not exist." %player1 , status=status.HTTP_400_BAD_REQUEST)

            # player2
            try:
                matched2 = Player.objects.get(pk=player2)
                old_gold2 = matched2.gold_total
                old_score2 = matched2.score

            except Player.DoesNotExist:
                return Response("Player2 '%s' does not exist." %player2 , status=status.HTTP_400_BAD_REQUEST)

            # player3
            try:
                matched3 = Player.objects.get(pk=player3)
                old_gold3 = matched3.gold_total
                old_score3 = matched3.score

            except Player.DoesNotExist:
                return Response("Player3 '%s' does not exist." %player3 , status=status.HTTP_400_BAD_REQUEST)

            # player4
            try:
                matched4 = Player.objects.get(pk=player4)
                old_gold4 = matched4.gold_total
                old_score4 = matched4.score

            except Player.DoesNotExist:
                return Response("Player4 '%s' does not exist." %player4 , status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            # ?????????????????????????????????
            newGameRun = GameRun.objects.get(run_id=run_id)
            newGameRun.player1_start_gold = old_gold1
            newGameRun.player2_start_gold = old_gold2
            newGameRun.player3_start_gold = old_gold3
            newGameRun.player4_start_gold = old_gold4

            player1_win1 = player1_win
            player2_win1 = player2_win
            player3_win1 = player3_win
            player4_win1 = player4_win
            # ?????????????????????????????????????????????????????????????????????
            if player1_win != 0 or player2_win != 0 or player3_win != 0 or player4_win != 0:
                all_bonus = decimal.Decimal('0')    # ?????????5%??????
                banker_count1 = 0
                banker_count2 = 0
                banker_count3 = 0
                banker_count4 = 0
                if player1_win > 0:     # ??????
                    if player1 == banker_player:
                        banker_count1 = 1
                    all_bonus = Helpers().getAllBonus(player1_win)
                    player1_win1 -= all_bonus
                    # ????????????
                    newGameRun.player1_settle_gold = old_gold1 + decimal.Decimal(player1_win) - all_bonus
                    newGameRun.player2_settle_gold = old_gold2 + decimal.Decimal(player2_win)
                    newGameRun.player3_settle_gold = old_gold3 + decimal.Decimal(player3_win)
                    newGameRun.player4_settle_gold = old_gold4 + decimal.Decimal(player4_win)
                    # player1 ????????????
                    newGameRun.player1_corp_bonus = all_bonus
                    if all_bonus > 0:
                        Helpers().addGoldFlow(player1,"6",all_bonus,"admin")

                elif player2_win > 0:     # ??????
                    if player2 == banker_player:
                        banker_count2 = 1
                    all_bonus = Helpers().getAllBonus(player2_win)
                    player2_win1 -= all_bonus
                    # ????????????
                    newGameRun.player1_settle_gold = old_gold1 + decimal.Decimal(player1_win)
                    newGameRun.player2_settle_gold = old_gold2 + decimal.Decimal(player2_win) - all_bonus
                    newGameRun.player3_settle_gold = old_gold3 + decimal.Decimal(player3_win)
                    newGameRun.player4_settle_gold = old_gold4 + decimal.Decimal(player4_win)
                    # player2 ????????????
                    newGameRun.player2_corp_bonus = all_bonus
                    if all_bonus > 0:
                        Helpers().addGoldFlow(player2,"6",all_bonus,"admin")

                elif player3_win > 0:     # ??????
                    if player3 == banker_player:
                        banker_count3 = 1
                    all_bonus = Helpers().getAllBonus(player3_win)
                    player3_win1 -= all_bonus
                    # ????????????
                    newGameRun.player1_settle_gold = old_gold1 + decimal.Decimal(player1_win)
                    newGameRun.player2_settle_gold = old_gold2 + decimal.Decimal(player2_win)
                    newGameRun.player3_settle_gold = old_gold3 + decimal.Decimal(player3_win) - all_bonus
                    newGameRun.player4_settle_gold = old_gold4 + decimal.Decimal(player4_win)
                    # player3 ????????????
                    newGameRun.player3_corp_bonus = all_bonus
                    if all_bonus > 0:
                        Helpers().addGoldFlow(player3,"6",all_bonus,"admin")

                elif player4_win > 0:     # ??????
                    if player4 == banker_player:
                        banker_count4 = 1
                    all_bonus = Helpers().getAllBonus(player4_win)
                    player4_win1 -= all_bonus
                    # ????????????
                    newGameRun.player1_settle_gold = old_gold1 + decimal.Decimal(player1_win)
                    newGameRun.player2_settle_gold = old_gold2 + decimal.Decimal(player2_win)
                    newGameRun.player3_settle_gold = old_gold3 + decimal.Decimal(player3_win)
                    newGameRun.player4_settle_gold = old_gold4 + decimal.Decimal(player4_win) - all_bonus
                    # player4 ????????????
                    newGameRun.player4_corp_bonus = all_bonus
                    if all_bonus > 0:
                        Helpers().addGoldFlow(player4,"6",all_bonus,"admin")

                # ?????????????????????
                newGameRun.total_bonus = all_bonus
                
                # ????????????????????????????????????????????????????????????
                # ???????????????????????????????????????
                if player1_win1 != 0:
                    Helpers().procPlayerGold(player1, "5", 
                                            newGameRun.player1_settle_gold, 
                                            player1_win1)
                if player2_win1 != 0:
                    Helpers().procPlayerGold(player2, "5", 
                                            newGameRun.player2_settle_gold, 
                                            player2_win1)
                if player3_win1 != 0:
                    Helpers().procPlayerGold(player3, "5", 
                                            newGameRun.player3_settle_gold, 
                                            player3_win1)
                if player4_win1 != 0:
                    Helpers().procPlayerGold(player4, "5", 
                                            newGameRun.player4_settle_gold, 
                                            player4_win1)

                # ????????????????????????????????????????????????
                obj1 = Helpers().procPlayerGameRoom(player1, game_room_id, 
                                          banker_count1, player1_win, old_gold1, 
                                          newGameRun.player1_settle_gold,
                                          newGameRun.player1_corp_bonus)

                obj2 = Helpers().procPlayerGameRoom(player2, game_room_id, 
                                          banker_count2, player2_win, old_gold2, 
                                          newGameRun.player2_settle_gold,
                                          newGameRun.player2_corp_bonus)

                obj3 = Helpers().procPlayerGameRoom(player3, game_room_id, 
                                          banker_count3, player3_win, old_gold3, 
                                          newGameRun.player3_settle_gold,
                                          newGameRun.player3_corp_bonus)

                obj4 = Helpers().procPlayerGameRoom(player4, game_room_id, 
                                          banker_count4, player4_win, old_gold4, 
                                          newGameRun.player4_settle_gold,
                                          newGameRun.player4_corp_bonus)
                newGameRun.is_settle = True
                newGameRun.last_modify_date = datetime.datetime.now()
                newGameRun.save()
                # ????????????????????????????????????
                msg = Helpers().procPlayerRoundResult(run_id)

                # print(f"[AddGameRunView]msg:{msg}")
            else:
                newGameRun.last_modify_date = datetime.datetime.now()
                newGameRun.save()

            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[[AddGameRunView(game_run)]2-done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            return Response(serializer.data)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GameRunDetailView(APIView):
    serializer_class = GameRunDetailSerializer
    permission_classes = (IsAuthenticated,)
      
    def get(self, request, run_id, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[GameRunDetailView(game_run/{run_id})-get]1-start =============================="
        logger1.warning(msg)
        #================================================================

        try:
            matchGameRun = GameRun.objects.get(run_id=run_id)
            serializer = GameRunDetailSerializer(matchGameRun, context={'request': request})

            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[GameRunDetailView(game_run/{run_id})-get]2-done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            return Response(serializer.data)
        except GameRun.DoesNotExist:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, run_id, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[GameRunDetailView(game_run/{run_id})-put]1-start =============================="
        logger1.warning(msg)
        #================================================================

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            run_id = serializer.validated_data.get('run_id')
            seqno_start_date = serializer.validated_data.get('seqno_start_date')
            run_name = serializer.validated_data.get('run_name')
            base = serializer.validated_data.get('base')
            points = serializer.validated_data.get('points')
            player1 = serializer.validated_data.get('player1')
            player2 = serializer.validated_data.get('player2')
            player3 = serializer.validated_data.get('player3')
            player4 = serializer.validated_data.get('player4')
            win_player = serializer.validated_data.get('win_player')
            lost_won_player = serializer.validated_data.get('lost_won_player')
            win_self_hand_player = serializer.validated_data.get('win_self_hand_player')
            banker_player = serializer.validated_data.get('banker_player')
            player1_win = serializer.validated_data.get('player1_win')
            player2_win = serializer.validated_data.get('player2_win')
            player3_win = serializer.validated_data.get('player3_win')
            player4_win = serializer.validated_data.get('player4_win')

            # Check existing account
            try:
                # Try to find the match player first
                matchGameRun = GameRun.objects.get(run_id=run_id)
                # ??????????????????????????????
                if not matchGameRun.is_settle:
                    matchGameRun.seqno_start_date = seqno_start_date
                    matchGameRun.run_name = run_name
                    matchGameRun.base = base
                    matchGameRun.points = points
                    matchGameRun.player1 = player1
                    matchGameRun.player2 = player2
                    matchGameRun.player3 = player3
                    matchGameRun.player4 = player4
                    matchGameRun.win_player = win_player
                    matchGameRun.lost_won_player = lost_won_player
                    matchGameRun.win_self_hand_player = win_self_hand_player

                    matchGameRun.player1_win = player1_win
                    matchGameRun.player2_win = player2_win
                    matchGameRun.player3_win = player3_win
                    matchGameRun.player4_win = player4_win

                    player1_win1 = player1_win
                    player2_win1 = player2_win
                    player3_win1 = player3_win
                    player4_win1 = player4_win
                    # player1
                    try:
                        matched1 = Player.objects.get(pk=player1)
                        old_gold1 = matched1.gold_total
                        old_score1 = matched1.score

                    except Player.DoesNotExist:
                        return Response("Player1 '%s' does not exist." %player1 , status=status.HTTP_400_BAD_REQUEST)

                    # player2
                    try:
                        matched2 = Player.objects.get(pk=player2)
                        old_gold2 = matched2.gold_total
                        old_score2 = matched2.score

                    except Player.DoesNotExist:
                        return Response("Player2 '%s' does not exist." %player2 , status=status.HTTP_400_BAD_REQUEST)

                    # player3
                    try:
                        matched3 = Player.objects.get(pk=player3)
                        old_gold3 = matched3.gold_total
                        old_score3 = matched3.score

                    except Player.DoesNotExist:
                        return Response("Player3 '%s' does not exist." %player3 , status=status.HTTP_400_BAD_REQUEST)

                    # player4
                    try:
                        matched4 = Player.objects.get(pk=player4)
                        old_gold4 = matched4.gold_total
                        old_score4 = matched4.score

                    except Player.DoesNotExist:
                        return Response("Player4 '%s' does not exist." %player4 , status=status.HTTP_400_BAD_REQUEST)

                    # ?????????????????????????????????????????????????????????????????????
                    if player1_win != 0 or player2_win != 0 or player3_win != 0 or player4_win != 0:
                        all_bonus = decimal.Decimal('0')    # ?????????5%??????
                        banker_count1 = 0
                        banker_count2 = 0
                        banker_count3 = 0
                        banker_count4 = 0
                        if player1_win > 0:     # ??????
                            if player1 == banker_player:
                                banker_count1 = 1
                            all_bonus = Helpers().getAllBonus(player1_win)
                            player1_win1 -= all_bonus
                            # ????????????
                            newGameRun.player1_settle_gold = old_gold1 + decimal.Decimal(player1_win) - all_bonus
                            newGameRun.player2_settle_gold = old_gold2 + decimal.Decimal(player2_win)
                            newGameRun.player3_settle_gold = old_gold3 + decimal.Decimal(player3_win)
                            newGameRun.player4_settle_gold = old_gold4 + decimal.Decimal(player4_win)
                            # player1 ????????????
                            newGameRun.player1_corp_bonus = all_bonus
                            if all_bonus > 0:
                                Helpers().addGoldFlow(player1,"6",all_bonus,"admin")

                        elif player2_win > 0:     # ??????
                            if player2 == banker_player:
                                banker_count2 = 1
                            all_bonus = Helpers().getAllBonus(player2_win)
                            player2_win1 -= all_bonus
                            # ????????????
                            newGameRun.player1_settle_gold = old_gold1 + decimal.Decimal(player1_win)
                            newGameRun.player2_settle_gold = old_gold2 + decimal.Decimal(player2_win) - all_bonus
                            newGameRun.player3_settle_gold = old_gold3 + decimal.Decimal(player3_win)
                            newGameRun.player4_settle_gold = old_gold4 + decimal.Decimal(player4_win)
                            # player2 ????????????
                            newGameRun.player2_corp_bonus = all_bonus
                            if all_bonus > 0:
                                Helpers().addGoldFlow(player2,"6",all_bonus,"admin")

                        elif player3_win > 0:     # ??????
                            if player3 == banker_player:
                                banker_count3 = 1
                            all_bonus = Helpers().getAllBonus(player3_win)
                            player3_win1 -= all_bonus
                            # ????????????
                            newGameRun.player1_settle_gold = old_gold1 + decimal.Decimal(player1_win)
                            newGameRun.player2_settle_gold = old_gold2 + decimal.Decimal(player2_win)
                            newGameRun.player3_settle_gold = old_gold3 + decimal.Decimal(player3_win) - all_bonus
                            newGameRun.player4_settle_gold = old_gold4 + decimal.Decimal(player4_win)
                            # player3 ????????????
                            newGameRun.player3_corp_bonus = all_bonus
                            if all_bonus > 0:
                                Helpers().addGoldFlow(player3,"6",all_bonus,"admin")

                        elif player4_win > 0:     # ??????
                            if player4 == banker_player:
                                banker_count4 = 1
                            all_bonus = Helpers().getAllBonus(player4_win)
                            player4_win1 -= all_bonus
                            # ????????????
                            newGameRun.player1_settle_gold = old_gold1 + decimal.Decimal(player1_win)
                            newGameRun.player2_settle_gold = old_gold2 + decimal.Decimal(player2_win)
                            newGameRun.player3_settle_gold = old_gold3 + decimal.Decimal(player3_win)
                            newGameRun.player4_settle_gold = old_gold4 + decimal.Decimal(player4_win) - all_bonus
                            # player4 ????????????
                            newGameRun.player4_corp_bonus = all_bonus
                            if all_bonus > 0:
                                Helpers().addGoldFlow(player4,"6",all_bonus,"admin")

                        # ???????????????????????????????????????
                        newGameRun.total_bonus = all_bonus

                        # ????????????????????????????????????????????????????????????
                        # ???????????????????????????????????????
                        if player1_win1 != 0:
                            Helpers().procPlayerGold(player1, "5", 
                                                    newGameRun.player1_settle_gold, 
                                                    player1_win1)
                        if player2_win1 != 0:
                            Helpers().procPlayerGold(player2, "5", 
                                                    newGameRun.player2_settle_gold, 
                                                    player2_win1)
                        if player3_win1 != 0:
                            Helpers().procPlayerGold(player3, "5", 
                                                    newGameRun.player3_settle_gold, 
                                                    player3_win1)
                        if player4_win1 != 0:
                            Helpers().procPlayerGold(player4, "5", 
                                                    newGameRun.player4_settle_gold, 
                                                    player4_win1)

                        # ????????????????????????????????????????????????
                        obj1 = Helpers().procPlayerGameRoom(player1, game_room_id, 
                                                banker_count1, player1_win, old_gold1, 
                                                newGameRun.player1_settle_gold,
                                                newGameRun.player1_corp_bonus)

                        obj2 = Helpers().procPlayerGameRoom(player2, game_room_id, 
                                                banker_count2, player2_win, old_gold2, 
                                                newGameRun.player2_settle_gold,
                                                newGameRun.player2_corp_bonus)

                        obj3 = Helpers().procPlayerGameRoom(player3, game_room_id, 
                                                banker_count3, player3_win, old_gold3, 
                                                newGameRun.player3_settle_gold,
                                                newGameRun.player3_corp_bonus)

                        obj4 = Helpers().procPlayerGameRoom(player4, game_room_id, 
                                                banker_count4, player4_win, old_gold4, 
                                                newGameRun.player4_settle_gold,
                                                newGameRun.player4_corp_bonus)
                        newGameRun.is_settle = True
                        newGameRun.last_modify_date = datetime.datetime.now()
                        newGameRun.save()
                        # ????????????????????????????????????
                        msg = Helpers().procPlayerRoundResult(run_id)
                        # print(f"[AddGameRunView]msg:{msg}")

                    else:
                        # ????????????????????????????????????
                        newGameRun.last_modify_date = datetime.datetime.now()
                        newGameRun.save()

                serializer = GameRunDetailSerializer(matchGameRun, context={'request': request})

                #================================================================
                d2=datetime.datetime.now()
                diff = (d2 - d1).total_seconds()
                msg = f"[GameRunDetailView(game_run/{run_id})-put]2-done,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                return Response(serializer.data)
            except GameRun.DoesNotExist:
                return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameRunListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, game_room_id, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[GameRunListView(game_run_List/{game_room_id})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        # Filter data based on input parameters
        result = GameRoom.objects.filter(game_room_id=game_room_id)
        serializer = GameRunDetailSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[GameRunListView(game_run_List/{game_room_id})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)


class GameRunListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, game_room_id, start_date, end_date, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[GameRunListWithDateView(game_run_List/{game_room_id}/{start_date}/{end_date})]1-start =============================="
        logger1.warning(msg)
        #================================================================
        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")

        # Filter data based on input parameters
        result = GameRoom.objects.filter(game_room_id=game_room_id, created_date__range=(start_date1, end_date1))
        serializer = GameRunDetailSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[GameRunListWithDateView(game_run_List/{game_room_id}/{start_date}/{end_date})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

# ????????????
class AddAgentView(APIView):
    serializer_class = AgentSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            player_id = serializer.validated_data.get('agent_player_id')
            try:
                # Find the match player first 
                matchPlayer = Player.objects.get(id=player_id)
                
                post_instance = serializer.save()
                datetime1 = post_instance.created_date
                post_instance.last_modify_date = datetime1
                post_instance.save()

                return Response(serializer.data)
                
            except Player.DoesNotExist:
                return Response("Player '%s' does not exist." % player_id, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AgentDetailView(APIView):
    serializer_class = UpdateAgentSerializer
    permission_classes = (IsAuthenticated,)
      
    def get(self, request, agent_player_id, format=None):
        try:
            matchAgent = AgentInfo.objects.get(agent_player_id=agent_player_id)
            serializer = UpdateAgentSerializer(matchAgent, context={'request': request})
            return Response(serializer.data)
        except AgentInfo.DoesNotExist:
            return Response("??????ID '%s' does not exist." % agent_player_id, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            agent_player_id = serializer.validated_data.get('agent_player_id')
            commisson_pc = serializer.validated_data.get('commisson_pc')
            remain_commisson = serializer.validated_data.get('remain_commisson')
            child_player_count = serializer.validated_data.get('child_player_count')
            child_player_total_run = serializer.validated_data.get('child_player_total_run')
            child_agent_player = serializer.validated_data.get('child_agent_player')

            # Check existing account
            try:
                # Try to find the match player first
                matchAgent = AgentInfo.objects.get(pk=pk)
                matchAgent.commisson_pc = commisson_pc
                matchAgent.remain_commisson = remain_commisson
                matchAgent.child_player_count = child_player_count
                matchAgent.child_player_total_run = child_player_total_run
                matchAgent.child_agent_player = child_agent_player
                matchAgent.last_modify_date = datetime.datetime.now()
                matchAgent.save()

                serializer = AgentSerializer(matchAgent, context={'request': request})
                return Response(serializer.data)

            except AgentInfo.DoesNotExist:
                return Response("??????ID '%s' does not exist." % agent_player_id, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ???????????????
class AddAccountView(APIView):
    serializer_class = NewAccountSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            useraccount = serializer.validated_data.get('user_account')
            level = serializer.validated_data.get('level')
            playerid = serializer.validated_data.get('player_id')
            createuser = serializer.validated_data.get('create_user')
            # ????????????(level)?????????????????????????????????ID????????????
            if level == '1':
                if playerid is None:
                    return Response("?????? ???%s' ???????????????????????????????????????ID???????????????" % useraccount, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if Helpers().checkAgentPlayer(playerid):
                        return Response("????????????ID '%s' ????????????" % playerid, status=status.HTTP_400_BAD_REQUEST)

            # Check existing account (????????????????????????)
            if Account.objects.filter(user_account=useraccount).count() != 0:
                return Response("?????? ???%s' ???????????????" % useraccount, status=status.HTTP_400_BAD_REQUEST)

            # Check ??????????????????????????????
            if Account.objects.filter(user_account=createuser).count() == 0:
                return Response("??????????????? ???%s' ????????????" % createuser, status=status.HTTP_400_BAD_REQUEST)

            post_instance = serializer.save()
            datetime1 = post_instance.created_date
            post_instance.modify_user = useraccount
            post_instance.last_modify_date = datetime1
            post_instance.save()

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountListView(APIView):
    permission_classes = (IsAuthenticated,)
      
    def get(self, request, format=None):
        try:
            queryset = Account.objects.all().order_by('id')
            serializer_class = AccountSerializer
            permission_classes = (IsAuthenticated,)
            
            serializer = AccountSerializer(queryset,many=True, context={'request': request})
            return Response(serializer.data)
        except Account.DoesNotExist:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

class AccountDetailView(APIView):
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
      
    def get(self, request, user_account, format=None):
        # print("AccountDetailView:user_account" + user_account)
        try:
            match_account = Account.objects.get(user_account=user_account)
            serializer = AccountSerializer(match_account, context={'request': request})
            return Response(serializer.data)
        except Account.DoesNotExist:
            return Response("????????? '%s' ??????????????????" % user_account, status=status.HTTP_400_BAD_REQUEST)


class UpdateAccountView(APIView):
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
      
    def put(self, request, pk, modify_user, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            useraccount = serializer.validated_data.get('user_account')
            username = serializer.validated_data.get('user_name')
            phonenumber = serializer.validated_data.get('phone_number')
            level = serializer.validated_data.get('level')
            player_id = serializer.validated_data.get('player_id')

            if level == '1':
                if playerid is None:
                    return Response("?????? ???%s' ???????????????????????????????????????ID???????????????" % useraccount, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if Helpers().checkAgentPlayer(playerid):
                        return Response("????????????ID '%s' ????????????" % playerid, status=status.HTTP_400_BAD_REQUEST)

            try:

                match_account = Account.objects.get(pk=pk)
                match_account.user_name = username
                match_account.phone_number = phonenumber
                match_account.level = level
                match_account.player_id = player_id
                match_account.modify_user = modify_user
                match_account.last_modify_date = datetime.datetime.now()
                match_account.save()

                serializer = AccountSerializer(match_account, context={'request': request})
                return Response(serializer.data)
            except Account.DoesNotExist:
                return Response("????????? '%s' ??????????????????" % useraccount, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    #serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, old_pwd, new_pwd, modify_user , format=None):
        #serializer = self.serializer_class(data=request.data)

        #if serializer.is_valid():
        #    old_password = serializer.data.get('old_password')
        #    new_password = serializer.data.get('new_password')
        #    modify_user = serializer.data.get('modify_user')

            # print("ChangePasswordView:")
            # print("pk:"+str(pk))
            # print("old password:"+old_pwd)
            # print("new password:"+new_pwd)
            # print("modify_user:"+modify_user)

            try:
                match_account = Account.objects.get(pk=pk)
                useraccount = match_account.user_account
                account_pwd = match_account.user_password
                # print("old password1:"+account_pwd)
                if old_pwd != account_pwd:
                    return Response("????????????????????????", status=status.HTTP_400_BAD_REQUEST)
            
                match_account.user_password = new_pwd
                match_account.modify_user = modify_user
                match_account.last_modify_date = datetime.datetime.now()
                match_account.save()

                # ????????????????????????
                createdObj = Helpers().addChangePWDData(useraccount, old_pwd, new_pwd, modify_user)


                return Response("????????? '%s' ?????????????????????" % useraccount, status=status.HTTP_202_ACCEPTED)
            except Account.DoesNotExist:
                return Response("???????????????????????????", status=status.HTTP_400_BAD_REQUEST)
        
        #else:
        #    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, modify_user , format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                match_account = Account.objects.get(pk=pk)
                useraccount = match_account.user_account

                datetime1 = datetime.datetime.now()

                match_account.is_delete = True
                match_account.deleted_user = modify_user
                match_account.deleted_date = datetime1

                match_account.modify_user = modify_user
                match_account.last_modify_date = datetime1

                match_account.save()

                serializer = AccountSerializer(match_account, context={'request': request})
                return Response(serializer.data)
            except Account.DoesNotExist:
                return Response("???????????????????????????", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ????????????
class CheckLoginView(APIView):
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, user_account, user_password, login_system, format=None):
        d1=datetime.datetime.now()
        msg = f"[CheckLoginView(check_login)]1-start =============================="
        logger1.warning(msg)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if login_system != 1 and login_system != 2:
                return Response("login_system ?????????" , status=status.HTTP_400_BAD_REQUEST)

            try:
                match_account = Account.objects.get(user_account=user_account)
                level = match_account.level
                delete_mark = match_account.is_delete
                pwd = match_account.user_password

                if delete_mark == True:
                    return Response("?????? '%s' ??????????????????" % user_account, status=status.HTTP_400_BAD_REQUEST)

                if login_system == 1 and level == 2:
                    return Response("?????? '%s' ??????????????????" % user_account, status=status.HTTP_400_BAD_REQUEST)

                if pwd != user_password:
                    return Response("?????? '%s' ???????????????" % user_account, status=status.HTTP_400_BAD_REQUEST)
                
                # ??????????????????
                createdObj = Helpers().addLoginData(user_account, login_system)
                last_login_date = createdObj.login_date
                match_account.last_login_date = last_login_date

                match_account.save()

                serializer = AccountSerializer(match_account, context={'request': request})
                return Response(serializer.data)
            except Account.DoesNotExist:
                return Response("???????????????????????????" % user_account, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ?????????????????????
class PlayerBindView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def put(self, request,player_id, bindcode, format=None):
        # print(f'[PlayerBindView]player_id:{player_id}, bindcode:{bindcode}')
        # Check player exist
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerBindView(player_bind/{player_id}/{bindcode})]1-start =============================="
        logger1.warning(msg)
        #================================================================
        try:
            # Try to find the match player first
            matched = Player.objects.get(id=player_id)
            # Check bindcode's player exist(bind with player_id)
            bind_player = Helpers().get_player_bind_player(bindcode)
            #if not Helpers().isPlayerExist(bindcode) == True:
            if bind_player == 0:
                return Response("??????????????????'%s'????????????" % bindcode, status=status.HTTP_400_BAD_REQUEST)

            if bindcode is not None and len(bindcode) > 0:
                matched.bindcode = bindcode
                matched.bind_player = bind_player

            matched.last_modify_date = datetime.datetime.now()
            matched.save()
            serializer = PlayerBindSerializer(matched, context={'request': request})

            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerBindView(player_bind/{player_id}/{bindcode})]2-done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            return Response(serializer.data)

        except Player.DoesNotExist:
            return Response("Player '%s' does not exist." % player_id, status=status.HTTP_400_BAD_REQUEST)

# VIP ??????
class VipStoredValueView(APIView):
    serializer_class = VipStoredValueSerializer
    permission_classes = (IsAuthenticated,)
    error_msg = ""
    def put(self, request, player_id, vip_type , format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]1-start ============================="
        logger1.warning(msg)
        #================================================================
        # Check existing account
        try:
            # ??????vip??????????????????????????????
            star = Helpers().transferStar(vip_type)
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]2-??????vip??????????????????????????????,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            # Try to find the match player first
            matched = Player.objects.get(id=player_id)

            if vip_type not in (1,2,3,4,5,6):
                #================================================================
                d3=datetime.datetime.now()
                diff = (d3 - d2).total_seconds()
                msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]r1-????????????VIP?????????,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                error_msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]????????????VIP?????????"
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

            # ?????????????????????????????????
            if matched.star < star:
                #================================================================
                d4=datetime.datetime.now()
                diff = (d4 - d2).total_seconds()
                msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]r2-???????????????,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                error_msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]???????????????"
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

            next_vip = matched.vip_type + 1
            if vip_type > next_vip:
                #================================================================
                d5=datetime.datetime.now()
                diff = (d5 - d2).total_seconds()
                msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]r3-?????????????????????,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                error_msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]?????????????????????"
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
            # vip ?????????
            if vip_type > matched.vip_type:
                matched.vip_type = vip_type

            matched.last_modify_date = datetime.datetime.now()
            matched.save()
            #================================================================
            d6=datetime.datetime.now()
            diff = (d6 - d2).total_seconds()
            msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]3-player data save,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            # ?????????????????????????????????????????????
            Helpers().procPlayerStar(player_id, 99999999, "1", star)
            #================================================================
            d7=datetime.datetime.now()
            diff = (d7 - d6).total_seconds()
            msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]4-?????????????????????????????????????????????,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            # ??????????????????player?????????????????????
            matched = Player.objects.get(id=player_id)
            #================================================================
            d8=datetime.datetime.now()
            diff = (d8 - d7).total_seconds()
            msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]5-?????????player,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            # ?????????????????????????????????
            gold = Helpers().transferGold(vip_type)
            new_gold = matched.gold_total + gold
            matched.last_modify_date = datetime.datetime.now()
            matched.save()
            #================================================================
            d9=datetime.datetime.now()
            diff = (d9 - d8).total_seconds()
            msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]6-?????????????????????????????????????????? player,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            # print(f'[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]old_gold:{matched.gold_total}, gold:{gold}, new_gold:{new_gold}')
            # ?????????????????????????????????
            Helpers().procPlayerGold(player_id, "1",
                                     new_gold, 
                                     gold)
            #================================================================
            d10=datetime.datetime.now()
            diff = (d10 - d9).total_seconds()
            msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]7-??????????????????,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            # ???????????????
            refData = Helpers().getRefSeat(vip_type, player_id)
            #================================================================
            d11=datetime.datetime.now()
            diff = (d11 - d10).total_seconds()
            msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]8-???????????????,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            ref_seat = refData['ref_seat']
            bind_player = refData['bind_player']
            isNewVip = refData['isNewVip']
            if ref_seat > 0:    
                # ????????????????????????
                pSeat = Helpers().getParentSeat(vip_type, ref_seat)
                #================================================================
                d12=datetime.datetime.now()
                diff = (d12 - d11).total_seconds()
                msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]8-????????????????????????,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                # ???????????????
                newSeat = Helpers().addNewSeat(vip_type, player_id, 
                                               bind_player, pSeat)
                #================================================================
                d13=datetime.datetime.now()
                diff = (d13 - d12).total_seconds()
                msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]8-???????????????,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================
                # ??????????????????Player1???????????????
                if isNewVip:
                    Helpers().modifyFirstSeat(vip_type, player_id, newSeat)
                    #================================================================
                    d13_1=datetime.datetime.now()
                    diff = (d13_1 - d13).total_seconds()
                    msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]8.1-??????????????????Player1???????????????,spent : {diff} seconds"
                    logger1.warning(msg)
                    #================================================================

                # ?????????????????????????????????
                Helpers().procStarBonus(player_id, vip_type, newSeat)
                
                #================================================================
                d14=datetime.datetime.now()
                diff = (d14 - d13).total_seconds()
                msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]9-?????????????????????????????????,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

            else: # ??????????????????
                newSeat = Helpers().getNewSeat(vip_type)
                #================================================================
                d15=datetime.datetime.now()
                diff = (d15 - d11).total_seconds()
                msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]9-??????????????????,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                newvip = VIPTree.objects.create(
                    vip_type = vip_type,
                    seat = newSeat,
                    layer = 1,
                    parent = 0,
                    player_id = player_id,
                    bind_player = 0
                )
                # ??????????????????
                Helpers().modifyFirstSeat(vip_type,player_id,newSeat)
                #================================================================
                d16=datetime.datetime.now()
                diff = (d16 - d15).total_seconds()
                msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]10-??????????????????,spent : {diff} seconds"
                logger1.warning(msg)

            d17=datetime.datetime.now()
            # ????????? procPlayerGold ???????????????????????????????????????????????????????????????db??????
            matched = Player.objects.get(id=player_id)
            serializer = VipStoredValueSerializer(matched, context={'request': request})

            #================================================================
            d18=datetime.datetime.now()
            diff = (d18 - d17).total_seconds()
            msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            
            return Response(serializer.data)

        except Player.DoesNotExist:
            #================================================================
            d2_1=datetime.datetime.now()
            diff = (d2_1 - d1).total_seconds()
            msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]Player {player_id} does not exist,spent : {diff} seconds"
            logger1.debug(msg)
            #================================================================

            error_msg = f"[VipStoredValueView(vip_store_value/{player_id}/{vip_type})]Player {player_id} does not exist."
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

# ??????????????????????????????
class PlayerJewelView(APIView):
    serializer_class = PlayerJewelViewSerializer
    permission_classes = (IsAuthenticated,)
      
    def get(self, request, player_id, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerJewelView(get_player_jewels/{player_id})]1-start =============================="
        logger1.warning(msg)
        #================================================================
        try:
            matched = Player.objects.get(id=player_id)
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerJewelView(get_player_jewels/{player_id})]2-get db data,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            serializer = PlayerJewelViewSerializer(matched, context={'request': request})
            #================================================================
            d3=datetime.datetime.now()
            diff = (d3 - d2).total_seconds()
            msg = f"[PlayerJewelView(get_player_jewels/{player_id})]3-data serialize,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================

            return Response(serializer.data)
        except Player.DoesNotExist:
            #================================================================
            d3=datetime.datetime.now()
            diff = (d3 - d1).total_seconds()
            msg = f"[PlayerJewelView(get_player_jewels/{player_id})]Player {player_id} does not exist,spent : {diff} seconds"
            logger1.debug(msg)
            #================================================================
            return Response("Player '%s' does not exist." %player_id , status=status.HTTP_400_BAD_REQUEST)

'''
  update bind player
'''
def updatebindPlayer(self):
    all_count = 0
    processed = 0
    #try:
    rs = Player.objects.filter(bindcode__isnull=False)
    all_count = rs.count()
    for d in rs:
        # print(f"[updatebindPlayer]bindcode:{d.bindcode}")
        if len(d.bindcode) > 0:
            bind_player = Helpers().get_player_bind_player(d.bindcode)
            # print(f"[updatebindPlayer]bind_player:{bind_player}")
            # ?????? player_id??????
            if bind_player == 0 and d.bindcode.isdigit():
                check_id = int(d.bindcode)
                # print(f"[updatebindPlayer]check_id:{check_id}")
                if Helpers().isPlayerExist(check_id):
                    bind_player = check_id
                    d.bind_player = bind_player
                    d.save()
                    processed = processed + 1

    #except:
    #    pass
    
    msg = f"Done~ (all count:{all_count}, processed:{processed})"
    return HttpResponse(msg,status=200)

'''
  ??????????????????
'''                  
class AddPlayerOrderView(APIView):
    serializer_class = PlayerOrderSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[AddPlayerOrderView(player_order)]1-start =============================="
        logger1.warning(msg)
        #================================================================

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            player_id = serializer.validated_data.get('player_id')
            wallet_addr = serializer.validated_data.get('wallet_addr')
            amount = serializer.validated_data.get('amount')

            #f'[AddPlayerOrderView]player_id:{player_id},wallet_addr:{wallet_addr}, amount:{amount}')

            if amount == 0:
                return Response("???????????????0???", status=status.HTTP_400_BAD_REQUEST)

            try:
                # Find the match player first 
                matched = Player.objects.get(id=player_id)
                # get player star
                old_star = matched.star
                if old_star < amount:
                  return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

                post_instance = serializer.save()
                post_instance.old_amount = old_star
                post_instance.save()
                # ?????????????????????????????????????????????????????????????????????
                # call procPlayerStar(????????????????????????????????????????????????)
                starflow_type = "7"
                Helpers().procPlayerStar(player_id, 99999999, starflow_type, amount)

                serializer1 = PlayerOrderListSerializer(post_instance, context={'request': request})

                #================================================================
                d2=datetime.datetime.now()
                diff = (d2 - d1).total_seconds()
                msg = f"[AddPlayerOrderView(player_order)]2-done,spent : {diff} seconds"
                logger1.warning(msg)
                #================================================================

                return Response(serializer1.data)

            except Player.DoesNotExist:
                return Response(f"Player {player_id} does not exist.", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlayerOrderListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, format=None ):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerOrderListView(player_order_List/{player_id})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        # Filter data based on input parameters
        result = PlayerOrder.objects.filter(player_id=player_id)
        serializer = PlayerOrderListSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("???????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[PlayerOrderListView(player_order_List/{player_id})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

'''
  ????????????????????????
'''
class PlayerStarListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, type, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerStarListView(player_star_List/{player_id}/{type})]1-start =============================="
        logger1.warning(msg)
        #================================================================
        # Filter data based on input parameters
        result = PlayerStar.objects.filter(player_id=player_id, star_type = type)
        serializer = PlayerStarSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[PlayerStarListView(player_star_List/{player_id}/{type})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

class PlayerStarListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, type, start_date, end_date, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerStarListWithDateView(player_star_ListbyDate/{player_id}/{type}/{start_date}/{end_date})]1-start =============================="
        logger1.warning(msg)
        #================================================================
        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
        
        # Filter data based on input parameters
        result = PlayerStar.objects.filter(player_id=player_id, star_type = type, created_date__range=(start_date1, end_date1))
        serializer = PlayerStarSerializer(result, many=True, context={'request': request})

        if result.count() == 0:
            return Response("?????????????????????", status=status.HTTP_400_BAD_REQUEST)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[PlayerStarListWithDateView(player_star_ListbyDate/{player_id}/{type}/{start_date}/{end_date})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return Response(serializer.data)

# ???????????????VIP??????????????????
def vip_count(request,vip_type):
    if request.method == 'GET':
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[vip_count/{vip_type}]1-start =============================="
        logger1.warning(msg)
        #================================================================

        vipcnt = Helpers().getVipCount(vip_type)
        result = {
            "match_count":vipcnt
        }

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[vip_count/{vip_type}]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return JsonResponse(result, safe=False)
    else:
        return Response("Only support GET method!!", status=status.HTTP_400_BAD_REQUEST) 

# ??????????????????
def player_member_list(request,player_id):
    if request.method == 'GET':
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[player_member_list/{player_id}]1-start =============================="
        logger1.warning(msg)
        #================================================================

        result = Helpers().player_member_list(player_id)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[player_member_list/{player_id}]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return JsonResponse(result, safe=False)
    else:
        return Response("Only support GET method!!", status=status.HTTP_400_BAD_REQUEST)

# ????????????????????????????????????
def player_fans_count(request, player_id, vip_type):
    if request.method == 'GET':
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[player_fans_count/{player_id}/{vip_type}]1-start =============================="
        logger1.warning(msg)
        #================================================================

        cnt = Helpers().player_fans_count(player_id,vip_type)
        result = {
            "match_count":cnt
        }

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[player_fans_count/{player_id}/{vip_type}]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return JsonResponse(result, safe=False)
    else:
        return Response("Only support GET method!!", status=status.HTTP_400_BAD_REQUEST)

# ???????????????????????????????????????
def player_member_count(request, player_id, vip_type):
    if request.method == 'GET':
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[player_member_count/{player_id}/{vip_type}]1-start =============================="
        logger1.warning(msg)
        #================================================================

        cnt = Helpers().player_member_count(player_id, vip_type)
        result = {
            "match_count":cnt
        }

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[player_member_count/{player_id}/{vip_type}]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return JsonResponse(result, safe=False)
    else:
        return Response("Only support GET method!!", status=status.HTTP_400_BAD_REQUEST)

# ??????????????????????????????????????????????????????
def player_vip_summary(request, player_id, vip_type):
    if request.method == 'GET':
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[player_vip_summary/{player_id}/{vip_type}]1-start =============================="
        logger1.warning(msg)
        #================================================================

        result = Helpers().player_vip_summary(player_id, vip_type)

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[player_vip_summary/{player_id}/{vip_type}]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return JsonResponse(result, safe=False)
    else:
        return Response("Only support GET method!!", status=status.HTTP_400_BAD_REQUEST)

# test
# def check1(self,checklayer):
#     if checklayer < 2:
#         base = 1
#     else:
#         base = pow(3,checklayer-1)

#     tmp = []
#     for i in range(3):
#         for j in range(base):
#             chkPos = 3 * j + i 
#             print(f"[check1]i:{i}, j:{j}, chkPos:{chkPos}")
#             tmp.append(chkPos)

#     print(f"[check1]tmp:{tmp}")    

#     return HttpResponse("Done~",status=200)

'''
  clear data
'''
def cleardata(self):
    all_count = 0
    processed = 0
    #try:
    rs = Player.objects.filter(bindcode__isnull=False)
    all_count = rs.count()
    for d in rs:
        # print(f"[updatebindPlayer]bindcode:{d.bindcode}")
        if len(d.bindcode) > 0:
            bind_player = Helpers().get_player_bind_player(d.bindcode)
            # print(f"[updatebindPlayer]bind_player:{bind_player}")
            # ?????? player_id??????
            if bind_player == 0 and d.bindcode.isdigit():
                check_id = int(d.bindcode)
                # print(f"[updatebindPlayer]check_id:{check_id}")
                if Helpers().isPlayerExist(check_id):
                    bind_player = check_id
                    d.bind_player = bind_player
                    d.save()
                    processed = processed + 1

    #except:
    #    pass
    
    msg = f"Done~ (all count:{all_count}, processed:{processed})"
    return HttpResponse(msg,status=200)

# ?????????????????? -> ???????????????????????????
class PlayerBuyChipsView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, player_id, amount, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerBuyChipsView(player_buychips/{player_id}/{amount})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        result = {}
        ret_msg = ""
        code = -1
        ret_amount = 0
        try:
            if decimal.Decimal(amount) != decimal.Decimal('0'):
                matched = Player.objects.get(id=player_id)
                old_amount = matched.gold_total
                new_amount = decimal.Decimal(amount)
                gold_type = "7"
                # ??????????????????
                newPlayerGold = PlayerGold.objects.create(
                    player_id = player_id, 
                    type = gold_type,
                    amount = new_amount * decimal.Decimal("-1"),
                    old_amount = old_amount
                )

                # ?????????????????????
                matched.gold_total -= new_amount
                matched.last_modify_date = datetime.datetime.now()
                matched.save()

                # ??????????????????
                Helpers().goldFlowProcess(player_id, gold_type ,new_amount,"ammin")
                ret_amount = matched.gold_total

            ret_msg = "success"
            result["code"] = 0
            result['msg'] = ret_msg
            result['amount'] = ret_amount

            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerBuyChipsView(player_buychips/{player_id}/{amount})]2-done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            
            return JsonResponse(result, safe=False)
            
        except Player.DoesNotExist:
            ret_msg = f"Player {player_id} does not exist."
            result["code"] = -1
            result['msg'] = ret_msg
            return JsonResponse(result, safe=False, status = status.HTTP_400_BAD_REQUEST)

# ??????????????????
#   1.???5%??????????????????
#   2.?????????????????????????????????
class PlayerRedeemView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, player_id, amount, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerRedeemView(player_redeem/{player_id}/{amount})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        result = {}
        ret_msg = ""
        code = -1
        ret_amount = 0
        try:
            amount1 = decimal.Decimal(amount)
            if amount1 != decimal.Decimal('0'):
                matched = Player.objects.get(id=player_id)
                old_amount = matched.gold_total
                # ????????????
                bonus = amount1 * decimal.Decimal('0.05')
                # ??????????????????????????????
                Helpers().goldFlowProcess(player_id, "6" ,bonus,"admin")

                new_amount = amount1 - bonus
                gold_type = "8"
                # ??????????????????
                newPlayerGold = PlayerGold.objects.create(
                    player_id = player_id, 
                    type = gold_type,
                    amount = new_amount,
                    old_amount = old_amount
                )

                # ?????????????????????
                matched.gold_total += new_amount
                matched.last_modify_date = datetime.datetime.now()
                matched.save()

                # ??????????????????
                Helpers().goldFlowProcess(player_id, gold_type ,new_amount,"admin")
                ret_amount = matched.gold_total

            ret_msg = "success"
            result["code"] = 0
            result['msg'] = ret_msg
            result['amount'] = ret_amount
            
            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerRedeemView(player_redeem/{player_id}/{amount})]2-done,spent : {diff} seconds"
            logger1.warning(msg)            
            #================================================================
            return JsonResponse(result, safe=False)
            
        except Player.DoesNotExist:
            ret_msg = f"Player {player_id} does not exist."
            result["code"] = -1
            result['msg'] = ret_msg
            return JsonResponse(result, safe=False, status = status.HTTP_400_BAD_REQUEST)

# ??????????????????(?????????)
#   ?????????????????????????????????
class PlayerRedeemNoBounsView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, player_id, amount, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerRedeemNoBounsView(player_redeem_no_bonus/{player_id}/{amount})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        result = {}
        ret_msg = ""
        code = -1
        ret_amount = 0
        try:
            amount1 = decimal.Decimal(amount)
            if amount1 != decimal.Decimal('0'):
                matched = Player.objects.get(id=player_id)
                old_amount = matched.gold_total
                new_amount = amount1
                gold_type = "8"
                # ??????????????????
                newPlayerGold = PlayerGold.objects.create(
                    player_id = player_id, 
                    type = gold_type,
                    amount = new_amount,
                    old_amount = old_amount
                )

                # ?????????????????????
                matched.gold_total += new_amount
                matched.last_modify_date = datetime.datetime.now()
                matched.save()

                # ??????????????????
                Helpers().goldFlowProcess(player_id, gold_type ,new_amount,"admin")
                ret_amount = matched.gold_total

            ret_msg = "success"
            result["code"] = 0
            result['msg'] = ret_msg
            result['amount'] = ret_amount

            #================================================================
            d2=datetime.datetime.now()
            diff = (d2 - d1).total_seconds()
            msg = f"[PlayerRedeemNoBounsView(player_redeem_no_bonus/{player_id}/{amount})]2-done,spent : {diff} seconds"
            logger1.warning(msg)
            #================================================================
            
            return JsonResponse(result, safe=False)
            
        except Player.DoesNotExist:
            ret_msg = f"Player {player_id} does not exist."
            result["code"] = -1
            result['msg'] = ret_msg
            return JsonResponse(result, safe=False, status = status.HTTP_400_BAD_REQUEST)


'''
  ??????????????????????????????
'''
class PlayerBonusListView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, type, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerBonusListView(player_bonus_List/{player_id}/{type})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        result = {}
        data = []
        ret_msg = ""
        if type=='1':      # ????????????
            rs1 = VIPBonus.objects.filter(level_player=player_id)
            for d1 in rs1:
                rs = {}
                rs['player_id'] = d1.player_id
                rs['nick_name'] = Helpers().get_player_nickname(d1.player_id)
                rs['date'] = datetime.datetime.strftime(d1.created_date, "%Y-%m-%d %H:%M:%S")
                rs['bouns'] = d1.level_bouns
                data.append(rs)
        elif type == '2':  # ????????????
            rs2 = VIPBonus.objects.filter(match_player=player_id)
            for d2 in rs2:
                rs = {}
                rs['player_id'] = d2.player_id
                rs['nick_name'] = Helpers().get_player_nickname(d2.player_id)
                rs['date'] = datetime.datetime.strftime(d2.created_date, "%Y-%m-%d %H:%M:%S")
                rs['bouns'] = d2.match_bonus
                data.append(rs)

        if len(data) > 0:
            result['code'] = 0
            result['msg'] = "success"
            result['data'] = data
            return JsonResponse(result, safe=False)
        else:
            result['code'] = -1
            result['msg'] = "????????????????????????"

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[PlayerBonusListView(player_bonus_List/{player_id}/{type})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return JsonResponse(result, safe=False, status = status.HTTP_400_BAD_REQUEST)

class PlayerBonusListWithDateView(APIView):
    permission_classes = (IsAuthenticated,)

    # @xframe_options_exempt
    def get(self, request, player_id, type,start_date, end_date, format=None):
        #================================================================
        d1=datetime.datetime.now()
        msg = f"[PlayerBonusListWithDateView(player_bonus_ListbyDate/{player_id}/{type}/{start_date}/{end_date})]1-start =============================="
        logger1.warning(msg)
        #================================================================

        start_date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        end_date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
        result = {}
        data = []
        ret_msg = ""
        if type=='1':      # ????????????
            rs1 = VIPBonus.objects.filter(level_player=player_id,created_date__range=(start_date1, end_date1))
            for d1 in rs1:
                rs = {}
                rs['player_id'] = d1.player_id
                rs['nick_name'] = Helpers().get_player_nickname(d1.player_id)
                rs['date'] = datetime.datetime.strftime(d1.created_date, "%Y-%m-%d %H:%M:%S")
                rs['bouns'] = d1.level_bouns
                data.append(rs)
        elif type == '2':  # ????????????
            rs2 = VIPBonus.objects.filter(match_player=player_id,created_date__range=(start_date1, end_date1))
            for d2 in rs2:
                rs = {}
                rs['player_id'] = d2.player_id
                rs['nick_name'] = Helpers().get_player_nickname(d2.player_id)
                rs['date'] = datetime.datetime.strftime(d2.created_date, "%Y-%m-%d %H:%M:%S")
                rs['bouns'] = d2.match_bonus
                data.append(rs)

        if len(data) > 0:
            result['code'] = 0
            result['msg'] = "success"
            result['data'] = data
            return JsonResponse(result, safe=False)
        else:
            result['code'] = -1
            result['msg'] = "????????????????????????"

        #================================================================
        d2=datetime.datetime.now()
        diff = (d2 - d1).total_seconds()
        msg = f"[PlayerBonusListWithDateView(player_bonus_ListbyDate/{player_id}/{type}/{start_date}/{end_date})]2-done,spent : {diff} seconds"
        logger1.warning(msg)
        #================================================================

        return JsonResponse(result, safe=False, status = status.HTTP_400_BAD_REQUEST)

'''
  ????????????
'''
# def test1(self):
#     d1=datetime.datetime.now()
#     msg = f"[test1(????????????)]1-start =============================="
#     logger1.warning(msg)

#     for i in range(0, 10000):
#         headers = {"Authorization": ": Basic c3VwZXJ1c2VyOjEyM2V3cWFzZGN4eg=="}
#         url = 'http://104.215.83.178:8010/gamecore/get_player_jewels/5/
#         # call api (post)
#         result = requests.get(url, data = "", headers = headers)

#     d2=datetime.datetime.now()
#     diff = (d2 - d1).total_seconds()
#     msg = f"[test1(????????????)]2-done,spent : {diff} seconds "
#     logger1.warning(msg)
#     return HttpResponse(msg,status=200)