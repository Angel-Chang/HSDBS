# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import webbrowser, json, time, re
import decimal

from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.db.models import Count, aggregates, Sum, Q
from django.views import View
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import send_mail, send_mass_mail
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib import messages

from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from gamecore.models import *
from gamecore.views import *
from member.models import *
from member.serializers import *
from gamecore.serializers import *

#from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt import authentication
#from rest_framework_simplejwt import views
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.clickjacking import xframe_options_exempt
from django import forms
from member.forms import LoginForm, PasswordChangeForm, LoginForm2
import hashlib
import logging

logger2 = logging.getLogger('member.views')

'''
  密碼加密
'''
def hash_code(s, salt='ivan'):
  h = hashlib.sha256()
  s = s + salt
  h.update(s.encode())
  return h.hexdigest()

'''
  首頁
'''
def index(request):
  d1=datetime.datetime.now()
  msg = f"[index]1-start ============================================"
  logger2.warning(msg)
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')
  # print("[index]Jump to index.html")
  return render(request, "member/index.html", )

'''
  公司抽水紀錄
'''
class CommissionView(View):

  # @xframe_options_exempt
  def get(self, request):
    #try:
    #search_month = request.GET.get("checkMonth", None)
    search_month = ""
    if 'checkMonth' in request.GET:
      search_month = request.GET['checkMonth']
      check_year = int(search_month[:4])
      check_month = int(search_month[-2:])
      # print(f"search_month1:{search_month}")
    else:
      today = datetime.datetime.now()
      search_month = "{}/{}".format(today.year, '{:0>2d}'.format(today.month))
      # print(f"[CommissionView]search_month2:{search_month}")
      check_year = today.year
      check_month = today.month

    # print(f"[CommissionView]check_year:{check_year}")
    # print(f"[CommissionView]check_month:{check_month}")
    result = {}
    rs = Helpers().get_company_bonus_by_month(search_month)

    # print(f"ret:{ret.Count}")
    if rs is None:
      # print(f"無當月金流紀錄～")
      result["checkedCommissionNotFound"] = True

    bonus = Helpers().get_current_company_bonus()

    result = {
      "rs1": rs,
      "current_year": bonus['current_year'],
      "current_month": bonus['current_month'],
      "this_year_company_bonus": format(bonus['this_year_company_bonus'],'0,.2f'),
      "this_month_company_bonus": format(bonus['this_month_company_bonus'],'0,.2f'),
    }
    return render(request, "member/commission.html", result, )

# 公司抽水紀錄月檔(by month)
def bonus_list(request):
  # print(f"call bonus_list")
  result = {}
  if request.is_ajax():
    # print("[bonus_list]from ajax")
    search_month = request.GET.get('checkMonth')
    check_year = int(search_month[:4])
    check_month = int(search_month[-2:])
    # print(f"[bonus_list]search_month:{search_month} check_year:{check_year} check_month:{check_month}")

    # 傳入格式為 YYYY/MM
    rs = Helpers().get_company_bonus_by_month(search_month)
    if rs is None:
      # print(f"無當月金流紀錄～")
      result["checkedCommissionNotFound"] = True

    # print(f"rs:{rs}")
    result['rs1'] = rs
  return JsonResponse(result)

# 公司抽水日檔明細(by hour)
def bonus_detail(request):
  # print(f"[bonus_detail]")
  result = {}
  if request.is_ajax():
    # print("[bonus_detail]from ajax")
    check_date = request.GET.get('check_date')
    # print(f"check_date:{check_date}")
    # 傳入格式為 YYYY-MM-DD
    rs = Helpers().get_company_bonus_by_date(check_date)
    # print(f"rs:{rs}")
    result['rs2'] = rs
  return JsonResponse(result)

'''
  系統金流管理
'''
def goldflow(request):
  # print("[goldflow]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')
    
  start_date = request.GET.get("startTime1",None)
  end_date = request.GET.get("endTime1",None)

  # print(f"[goldflow]start_date:{start_date} end_date:{end_date}")

  ret = GoldFlowSummary.objects.all()
  total_amount = 0
  available_amount = 0
  flow_amount = 0
  star_amount = 0

  for d in ret:
    total_amount = d.total_amount             # 發行總金額
    available_amount = d.available_amount     # 總可用餘額
    flow_amount = d.flow_amount               # 總流動金額

  # 鑽石總額
  star_amount = StarFlow.objects.aggregate(Sum('star'))['star__sum']
  # print(f"[goldflow]star_amount:{star_amount}")

  result = {}

  filters = Q()
  filters.connector = "AND"

  now = datetime.datetime.now()
  #今天
  today = now

  if start_date is not None and len(start_date) > 0:
    date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[goldflow]2.start_date:{date1} ")
    filters.children.append(("created_date__gte",date1))
  else:  #  預設抓一天
    yesterday = now - timedelta(days=1)
    date1 = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)
    # print(f"[goldflow]2.start_date:{date1} ")
    filters.children.append(("created_date__gte",date1))

  if end_date is not None and len(end_date) > 0:
    date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[goldflow]3.end_date:{date1}")
    filters.children.append(("created_date__lte",date1))
  else:
    date1 = today.replace(hour=23,minute=59,second=59,microsecond=999999)
    # print(f"[goldflow]2.start_date:{date1} ")
    filters.children.append(("created_date__lte",date1))

  # 發行紀錄
  ret1 = GoldFlow.objects.filter(filters).filter(Q(type="1")).order_by("id")
  data1 = []
  for d1 in ret1:
    rs1 = {}
    rs1['id'] = d1.id
    rs1['amount'] = format(d1.amount,',')
    rs1['admin_userid'] = d1.admin_account
    rs1['created_date'] = datetime.datetime.strftime(d1.created_date, "%Y-%m-%d %H:%M:%S")

    data1.append(rs1)

  # print(f"[goldflow]data1:{data1}")

  # 補幣紀錄
  ret2 = AddValue.objects.filter(filters
                               ).filter(Q(type="2")
                               ).order_by("id")
  data2 = []
  for d2 in ret2:
    rs2 = {}
    rs2['id'] = d2.id
    rs2['jewel'] = d2.get_jewel_type_display()
    rs2['admin_account'] = d2.admin_account
    rs2['player'] = Helpers().get_player_nickname(d2.player_id)
    rs2['gold'] = format(d2.gold,',')
    rs2['description'] = d2.description
    rs2['created_date'] = datetime.datetime.strftime(d2.created_date, "%Y-%m-%d %H:%M:%S")

    data2.append(rs2)

  # print(f"[goldflow]data2:{data2}")

  # 轉幣紀錄
  ret3 = TransferGold.objects.filter(filters).order_by("id")
  data3 = []
  for d3 in ret3:
    rs3 = {}
    rs3['id'] = d3.id
    rs3['jewel'] = d3.get_jewel_type_display()
    rs3['sender_id'] = d3.sender_id
    rs3['sender'] = Helpers().get_player_nickname(d3.sender_id)
    gold1 = format(d3.sender_gold,',')
    gold2 = format(d3.sender_gold+d3.amount,',')
    sender_gold = '${} ⟶ ${}'.format(gold1,gold2)
    rs3['sender_gold'] = sender_gold 
    rs3['receiver_id'] = d3.receiver_id
    rs3['receiver'] = Helpers().get_player_nickname(d3.receiver_id)
    gold1 = format(d3.receiver_gold,',')
    gold2 = format(d3.receiver_gold-d3.amount,',')
    receiver_gold = '${} ⟶ ${}'.format(gold1,gold2)
    rs3['receiver_gold'] = receiver_gold
    rs3['amount'] = format(d3.amount,',')
    rs3['created_date'] = datetime.datetime.strftime(d3.created_date, "%Y-%m-%d %H:%M:%S")

    data3.append(rs3)

    # print(f"[goldflow]data3:{data3}")

  # 玩家入金紀錄
  ret4 = AddValue.objects.filter(filters).filter(Q(type="8",jewel_type=2)).order_by("id")
  data4 = []
  for d4 in ret4:
    rs4 = {}
    rs4['id'] = d4.id
    rs4['admin_account'] = d4.admin_account
    rs4['player'] = Helpers().get_player_nickname(d4.player_id)
    rs4['gold'] = format(d4.gold,',')
    rs4['created_date'] = datetime.datetime.strftime(d4.created_date, "%Y-%m-%d %H:%M:%S")

    data4.append(rs4)

  # print(f"[goldflow]data4:{data4}")

  # 鑽石紀錄
  ret5 = StarFlow.objects.filter(filters).order_by("id")
  data5 = []
  for d5 in ret5:
    rs5 = {}
    rs5['id'] = d5.id
    rs5['star_type'] = d5.get_starflow_type_display()
    rs5['player_id'] = d5.player_id
    rs5['player'] = Helpers().get_player_nickname(d5.player_id)
    rs5['star'] = format(d5.star,',')
    rs5['created_date'] = datetime.datetime.strftime(d5.created_date, "%Y-%m-%d %H:%M:%S")

    data5.append(rs5)

  # print(f"[goldflow]data5:{data5}")

  result = {
    "rs1": data1,
    "rs2": data2,
    "rs3": data3,
    "rs4": data4,
    "rs5": data5,
    "total_amount": format(total_amount,','),
    "available_amount": format(available_amount,'0,.2f'),
    "flow_amount": format(flow_amount,'0,.2f'),
    "star_amount": format(star_amount,'0,.2f')
  }

  if request.is_ajax():
    # print(f"[goldflow]from ajax")
    return JsonResponse(result, safe=False)

  return render(request, "member/goldflow.html", result,)

# 系統金流管理-發行金幣
def addGold(request):
  # print("[addGold]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  if request.method == 'POST':
    admin_account = request.session.get('user_id',None)

    # print(f"[addGold]request data:{request.POST}")

    # amount = request.POST.get('amount')
    # user_password = request.POST.get('user_password')
    amount = request.POST['amount']
    user_password = request.POST['user_pwd']
    # print(f"[addGold]amount:{amount} user_password:{user_password}")

    ret_msg = ""
    try:
      matched = Account.objects.get(user_account=admin_account)
      total_amount = 0
      available_amount = 0
      # 檢查密碼是否相符
      if user_password != matched.user_password:
        ret_msg = "密碼不正確!!"
        # print(f"[addGold]error:{ret_msg}")
      else:
        if GoldFlowSummary.objects.all().count() == 0:
          summary = GoldFlowSummary()
        else:
          summary = GoldFlowSummary.objects.get(pk=1)
          total_amount = summary.total_amount
          available_amount = summary.available_amount

        new_goldflow = GoldFlow()
        new_goldflow.type = "1"
        new_goldflow.amount = amount
        new_goldflow.admin_account = admin_account
        new_goldflow.old_amount = available_amount
        new_goldflow.save()
        # 更新資料到GoldFlowSummary
        total_amount += int(amount)
        available_amount += int(amount)
        summary.total_amount = total_amount
        summary.available_amount = available_amount
        summary.last_modify_date = datetime.datetime.now()
        summary.save()
        ret_msg = "金幣發行成功。"
        # print(f"[addGold]{ret_msg}")

    except Account.DoesNotExist:
      ret_msg = "異動者的帳號 {} 不存在".format(admin_account)
      # print(f"[addGold]error:{ret_msg}")

    result = {'msg':ret_msg}
  
    # if request.is_ajax():
    #   print("[addGold]from ajax")
    #   return JsonResponse(result, safe=False)

  return render(request, "member/goldflow.html", result,)

'''
  出金申請
'''
def player_order(request):
  # print("[player_order]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  result = {}
  ret1 = PlayerOrder.objects.all().order_by("-created_date")

  total_amount = 0
  data = []
  for d in ret1:
    rs = {}
    rs['id'] = d.id
    rs['player_id'] = d.player_id
    rs['wallet_addr'] = d.wallet_addr
    rs['amount'] = d.amount
    rs['created_date'] = datetime.datetime.strftime(d.created_date, "%Y-%m-%d")
    rs['status'] = d.status
    rs['status_name'] = d.get_status_display()
    data.append(rs)

  # print(f"[player_order]data:{data}")

  result = {
    "rs1": data
  }

  if request.is_ajax():
    # print("[player_order]from ajax")
    return JsonResponse(result, safe=False)

  return render(request, "member/player_order.html", result,)

# 出金申請
def update_player_order(request):
  # print("[update_player_order]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  if request.method == 'POST':
    pk = request.POST['pk']
    done_user = request.session.get('user_id',None)
    # print(f"pk:{pk}, done_user:{done_user}")
    try:
      matched = PlayerOrder.objects.get(pk=pk)
      matched.done_user = done_user
      matched.status = '1'
      matched.done_date = datetime.datetime.now()
      matched.save()
      ret_msg = "作業完成。"

    except PlayerOrder.DoesNotExist:
      ret_msg = "資料不存在。"

    ret1 = PlayerOrder.objects.all().order_by("-created_date")

    total_amount = 0
    data = []
    for d in ret1:
      rs = {}
      rs['id'] = d.id
      rs['player_id'] = d.player_id
      rs['wallet_addr'] = d.wallet_addr
      rs['amount'] = d.amount
      rs['created_date'] = datetime.datetime.strftime(d.created_date, "%Y-%m-%d")
      rs['status'] = d.status
      rs['status_name'] = d.get_status_display()
      data.append(rs)

    result = {
      "rs1": data,
      'msg':ret_msg
    }

    if request.is_ajax():
      return JsonResponse(result, safe=False)

  return render(request, "member/player_order.html", result,)

'''
  玩家資訊-玩家列表
'''
def playerlist(request):
  # print("[playerlist]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  start_date = request.GET.get("startTime1",None)
  end_date = request.GET.get("endTime1",None)
  args = request.GET.get("args",None)

  # print(f"[playerlist]start_date:{start_date} end_date:{end_date} args:{args}")
  
  now = datetime.datetime.now()

  result = {}
  # 會員總人數
  all_count = Player.objects.all().count()
  # 今年遊玩人數
  q1 = Q()
  q1.connector = "AND"
  q1.children.append(("created_date__year",now.year))
  this_year_count = IPInfo.objects.filter(q1).count()
  # 本月遊玩人數
  # 本月第一天和最后一天
  this_month_start = datetime.datetime(now.year, now.month, 1)
  if now.month == 12:
    this_month_end = datetime.datetime(now.year+1, 1, 1) - timedelta(days=1)
  else:
    this_month_end = datetime.datetime(now.year, now.month + 1, 1) - timedelta(days=1)
  date_start = this_month_start.replace(hour=0,minute=0,second=0,microsecond=0)
  date_end = this_month_end.replace(hour=23,minute=59,second=59,microsecond=999999)
  q2 = Q()
  q2.connector = "AND"
  q2.children.append(("created_date__gte",date_start))
  q2.children.append(("created_date__lte",date_end))
  this_month_count = IPInfo.objects.filter(q2).count()
  # 本日註冊人數
  today = now
  date_start = today.replace(hour=0,minute=0,second=0,microsecond=0)
  date_end = today.replace(hour=23,minute=59,second=59,microsecond=999999)
  q3 = Q()
  q3.connector = "AND"
  q3.children.append(("created_date__gte",date_start))
  q3.children.append(("created_date__lte",date_end))
  this_month_count = IPInfo.objects.filter(q3).count()
  today_registers = Player.objects.filter(q3).count()
  # 每日平均上線人數
  # 已過天數
  year_first_day = datetime.datetime(now.year,1,1)
  days = (now - year_first_day).days
  if days < 1:
    days = 1
  day_avg_count = this_year_count / days

  # print(f"[playerlist]all_count:{all_count}")
  # print(f"[playerlist]this_year_count:{this_year_count}")
  # print(f"[playerlist]this_month_count:{this_month_count}")
  # print(f"[playerlist]today_registers:{today_registers}")
  # print(f"[playerlist]day_avg_count:{day_avg_count}")

  filters1 = Q()
  filters1.connector = "AND"
  if start_date is not None and len(start_date) > 0:
    date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[playerlist]start_date:{date1} ")
    filters1.children.append(("created_date__gte",date1))

  if end_date is not None and len(end_date) > 0:
    date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[playerlist]end_date:{date1}")
    filters1.children.append(("created_date__lte",date1))

  filters2 = Q()
  filters2.connector = "OR"
  if args is not None and len(args) > 0:
    if args.isdigit():
      filters2.children.append(("pk",args))

    filters2.children.append(("phone_number",args))
    filters2.children.append(("nick_name",args))

  if args is not None and len(args) > 0:
    if args.isdigit():
      filters2.children.append(("pk",args))

    filters2.children.append(("phone_number",args))
    filters2.children.append(("nick_name",args))

  ret1 = Player.objects.filter(filters1).filter(filters2).order_by('id')

  data = []
  for d in ret1:
    rs = {}
    rs['id'] = d.id
    rs['nick_name'] = d.nick_name
    rs['gold'] = format(d.gold_total,'0,.2f')
    rs['star'] = format(d.star,'0,.2f')
    rs['phone_number'] = d.phone_number
    rs['register_mac_addr'] = d.register_mac_addr
    rs['bind_playerid'] = d.bind_player
    rs['bind_playername'] = d.get_bind_player_name()
    # 計算歷史場數
    qc = Q()
    qc.connector = "AND"
    qc.children.append(("player_id",d.id))
    history_game_runs = PlayerRoundResult.objects.filter(qc).count()
    rs['history_game_runs'] = history_game_runs
    rs['score'] = d.score
    if d.last_login_date is not None:
      rs['last_login_date'] = datetime.datetime.strftime(d.last_login_date, "%Y-%m-%d %H:%M:%S")
    else:
      rs['last_login_date'] = ''

    rs['created_date'] = datetime.datetime.strftime(d.created_date, "%Y-%m-%d %H:%M:%S")
    rs['player_type'] = d.permission_type
    rs['permission_type'] = d.get_permission_type_display()
    if d.is_lock:
      rs['state'] = "1"
    else:
      rs['state'] = "0"

    data.append(rs)

  # print(f"[playerlist]data:{data}")
  result = {
    "rs1": data,
    "all_count": all_count,
    "this_year_count": this_year_count,
    "this_month_count": this_month_count,
    "today_registers": today_registers,
    "day_avg_count": format(day_avg_count,'0,.6f')
  }

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/playerlist.html", result,)

# 玩家列表-玩家資訊-個人
def player(request):
  # print("[player]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')
  
  player_id = request.GET.get("player_id",None)
  start_date = request.GET.get("startTime1",None)
  end_date = request.GET.get("endTime1",None)

  # print(f"[player]1.player_id:{player_id}")
  # print(f"[player]1.start_date:{start_date} end_date:{end_date}")

  result = {}

  # 個人資訊
  ret = Player.objects.get(pk = player_id)
  rs = {}
  rs['id'] = ret.id
  rs['nick_name'] = ret.nick_name
  # rs['gold'] = format(int(ret.gold_total),',')
  rs['gold'] = format(ret.gold_total,'0,.2f')
  rs['star'] = format(ret.star,'0,.2f')
  rs['phone_number'] = ret.phone_number
  rs['register_mac_addr'] = ret.register_mac_addr
  rs['bind_playerid'] = ret.bind_player
  rs['bind_playername'] = ret.get_bind_player_name()
  if ret.line_id is None:
    rs['line_id'] = ''
  else:  
    rs['line_id'] = ret.line_id

  # 計算歷史場數
  qc = Q()
  qc.connector = "AND"
  qc.children.append(("player_id",ret.id))
  history_game_runs = PlayerRoundResult.objects.filter(qc).count()
  rs['history_game_runs'] = history_game_runs
  rs['score'] = ret.score
  if ret.last_login_date is not None:
    rs['last_login_date'] = datetime.datetime.strftime(ret.last_login_date, "%Y-%m-%d %H:%M:%S")
  else:
    rs['last_login_date'] = ''

  rs['created_date'] = datetime.datetime.strftime(ret.created_date, "%Y-%m-%d %H:%M:%S")
  rs['player_type'] = ret.permission_type
  rs['permission_type'] = ret.get_permission_type_display()
  if ret.is_lock:
    rs['state'] = "1"
  else:
    rs['state'] = "0"

  filters = Q()
  filters.connector = "AND"

  now = datetime.datetime.now()
  #今天
  today = now

  if start_date is not None and len(start_date) > 0:
    date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[player]2.start_date:{date1} ")
    filters.children.append(("created_date__gte",date1))
  else:  #  預設抓一天
    yesterday = now - timedelta(days=1)
    date1 = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)
    # print(f"[goldflow]2.start_date:{date1} ")
    filters.children.append(("created_date__gte",date1))

  if end_date is not None and len(end_date) > 0:
    date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[player]3.end_date:{date1}")
    filters.children.append(("created_date__lte",date1))
  else:
    date1 = today.replace(hour=23,minute=59,second=59,microsecond=999999)
    # print(f"[goldflow]2.start_date:{date1} ")
    filters.children.append(("created_date__lte",date1))

  # 登入紀錄
  q1 = Q()
  q1.connector = "AND"
  q1.children.append(("type","1"))
  q1.children.append(("player_id",player_id))
  ret1 = IPInfo.objects.filter(filters).filter(q1).order_by("id")
  data1 = []
  for d1 in ret1:
    rs1 = {}
    rs1['id'] = d1.id
    rs1['login_ip'] = d1.ip
    rs1['created_date'] = datetime.datetime.strftime(d1.created_date, "%Y-%m-%d %H:%M:%S")

    data1.append(rs1)

  # 轉幣紀錄
  q2 = Q()
  q2.connector = "OR"
  q2.children.append(("sender_id",player_id))
  q2.children.append(("receiver_id",player_id))
  ret2 = TransferGold.objects.filter(filters).filter(q2).order_by("id")
  data2 = []
  for d2 in ret2:
    rs2 = {}
    rs2['id'] = d2.id
    rs2['jewel'] = d2.get_jewel_type_display()
    rs2['sender_id'] = d2.sender_id
    rs2['sender'] = Helpers().get_player_nickname(d2.sender_id)
    gold1 = format(d2.sender_gold,',')
    gold2 = format(d2.sender_gold-d2.amount,',')
    sender_gold = '${} ⟶ ${}'.format(gold1,gold2)
    rs2['sender_gold'] = sender_gold 
    rs2['receiver_id'] = d2.receiver_id
    rs2['receiver'] = Helpers().get_player_nickname(d2.receiver_id)
    gold1 = format(d2.receiver_gold,',')
    gold2 = format(d2.receiver_gold+d2.amount,',')
    receiver_gold = '${} ⟶ ${}'.format(gold1,gold2)
    rs2['receiver_gold'] = receiver_gold
    rs2['amount'] = format(d2.amount,',')
    rs2['created_date'] = datetime.datetime.strftime(d2.created_date, "%Y-%m-%d %H:%M:%S")

    data2.append(rs2)

  # 補幣紀錄
  q3 = Q()
  q3.connector = "AND"
  q3.children.append(("type","2"))
  q3.children.append(("player_id",player_id))
  ret3 = AddValue.objects.filter(filters).filter(q3).order_by("id")
                               
  data3 = []
  for d3 in ret3:
    rs3 = {}
    rs3['id'] = d3.id
    rs3['jewel'] = d3.get_jewel_type_display()
    rs3['admin_account'] = d3.admin_account
    rs3['player'] = Helpers().get_player_nickname(d3.player_id)
    rs3['gold'] = format(d3.gold,',')
    rs3['description'] = d3.description
    rs3['created_date'] = datetime.datetime.strftime(d3.created_date, "%Y-%m-%d %H:%M:%S")

    data3.append(rs3)

  # 金流異動
  q4 = Q()
  q4.connector = "AND"
  q4.children.append(("player_id",player_id))
  ret4 = PlayerGold.objects.filter(filters).filter(q4).order_by("id")
  data4 = []
  for d4 in ret4:
    rs4 = {}
    rs4['id'] = d4.id
    rs4['tradetype'] = d4.get_type_display()
    rs4['amount'] = format(d4.amount,'0,.6f')
    # 金流異動欄位
    gold1 = format(d4.old_amount,'0,.2f')
    gold2 = format(d4.old_amount+d4.amount,'0,.2f')
    goldflow = '${} ⟶ ${}'.format(gold1,gold2)
    rs4['goldflow'] = goldflow
    rs4['created_date'] = datetime.datetime.strftime(d4.created_date, "%Y-%m-%d %H:%M:%S")

    data4.append(rs4)

  # 歷史場次
    # columns: [{field: 'id', title: 'ID', visible: false}, 
    #           {field: 'gametype', title: '遊戲類型'}, 
    #           {field: 'run_id', title: '遊戲局號'}, 
    #           {field: 'created_date', title: '日期'},
    #           {field: 'detail', title: '詳細'}]
  q5 = Q()
  q5.connector = "OR"
  q5.children.append(("player1",player_id))
  q5.children.append(("player2",player_id))
  q5.children.append(("player3",player_id))
  q5.children.append(("player4",player_id))
  ret5 = GameRun.objects.filter(filters).filter(q5
                              ).values('run_id','base','game_room', 
                                       'game_room__room',
                                       'game_room__room_create_date', 
                                       'game_room__area', 
                                       'game_room__state',
                                       'game_room__points', 
                                       'game_room__total_commission')
  data5 = []
  for d5 in ret5:
    rs5 = {}
    rs5['run_id'] = d5['run_id']  # 遊戲局號(回播碼)，GameRun's pk
    rs5['gametype'] = d5['base']
    area_str = Helpers().get_gamerun_area(d5['run_id'])
    area = '{}({}/{})'.format(area_str,d5['base'],d5['game_room__points'])
    rs5['area'] = area
    state = Helpers().get_gamerun_state(d5['run_id'])
    rs5['state'] = state
    all_bonus = d5['game_room__total_commission']
    rs5['all_bonus'] = all_bonus
    rs5['created_date'] = datetime.datetime.strftime(d5['game_room__room_create_date'], "%Y-%m-%d %H:%M:%S")
    rs5['detail'] = d5['run_id']

    data5.append(rs5)

  # 鑽石紀錄
  ret6 = PlayerStar.objects.filter(filters).filter(q4).order_by("id")
  data6 = []
  for d6 in ret6:
    rs6 = {}
    rs6['id'] = d6.id
    rs6['star_type'] = d6.get_star_type_display()
    # 鑽石異動欄位
    rs6['star'] = format(d6.star,',')
    # 鑽石異動欄位
    star1 = format(d6.old_star,'0,.2f')
    star2 = format(d6.old_star+d6.star,'0,.2f')
    starflow = '${} ⟶ ${}'.format(star1,star2)
    rs6['starflow'] = starflow
    rs6['created_date'] = datetime.datetime.strftime(d6.created_date, "%Y-%m-%d %H:%M:%S")

    data6.append(rs6)

  # print(f"[player]data1:{data1}")
  # print(f"[player]data2:{data2}")
  # print(f"[player]data3:{data3}")
  # print(f"[player]data4:{data4}")
  # print(f"[player]data5:{data5}")
  # print(f"[player]data6:{data6}")

  admin_account = request.session.get('user_id','')
  result = {
    "data": rs,
    "admin_account": admin_account,
    "rs1": data1,
    "rs2": data2,
    "rs3": data3,
    "rs4": data4,
    "rs5": data5,
    "rs6": data6
  }

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/player.html", result,)

# 玩家列表-玩家資訊-個人-修改身份
def modify_player_type(request):
  # print("[modify_player_type]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  if request.method == 'POST':
    admin_account = request.session.get('user_id',None)

    # print(f"[modify_player_type]request data:{request.POST}")
    player_id = request.POST['player_id']
    player_state = request.POST['player_state'] # 會員狀態
    player_type = request.POST['player_type']   # 會員身份
    user_pwd = request.POST['user_pwd']
    # print(f"[modify_player_type]player_id:{player_id} player_state:{player_state}")
    # print(f"[modify_player_type]player_type:{player_type} user_pwd:{user_pwd}")

    # 檢查密碼是否相符
    ret_msg = Helpers().isPasswordCorrect(admin_account,user_pwd)
    if len(ret_msg) == 0:    # 表示密碼比對ＯＫ
      # check player is exist or not
      if player_id is not None and len(player_id) > 0 and player_id.isdigit():
        try:
          matched_player = Player.objects.get(pk=player_id)
          # 更新會員狀態
          if player_state == "1":   # 鎖定
            matched_player.is_lock = True
          else:
            matched_player.is_lock = False
          # 更新會員身份
          matched_player.permission_type = player_type
          matched_player.last_modify_date = datetime.datetime.now()
          matched_player.save()

          ret_msg = "資料修改成功。"

        except Player.DoesNotExist:
          ret_msg = "玩家ID {} 不存在".format(player_id)
      else:
        ret_msg = "玩家ID {} 格式不正確".format(player_id)

    result = {'msg':ret_msg}
    # print(f"[modify_player_type]result:{result}")
    if request.is_ajax():
      # print("[modify_player_type]from ajax")
      return JsonResponse(result, safe=False)

  return render(request, "member/player.html", result,)

# 玩家列表-玩家資訊-個人-補幣/入金
def addvalue(request):
  # print("[addvalue]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  if request.method == 'POST':
    admin_account = request.session.get('user_id',None)

    # print(f"[modify_player_type]request data:{request.POST}")
    player_id = request.POST['player_id']
    amount = request.POST['amount']
    desc = request.POST['desc']
    addvalue_type = request.POST['addvalue_type']
    jewel_type = request.POST['jewel_type']
    user_pwd = request.POST['user_pwd']
    # print(f"[addvalue]addvalue_type:{addvalue_type} user_pwd:{user_pwd}")
    # print(f"[addvalue]jewel_type:{jewel_type}")

    # 檢查密碼是否相符
    ret_msg = Helpers().isPasswordCorrect(admin_account,user_pwd)
    new_gold = decimal.Decimal(0)
    new_star = decimal.Decimal(0)
    if len(ret_msg) == 0:    # 表示密碼比對ＯＫ
      # check player is exist or not
      if player_id is not None and len(player_id) > 0 and player_id.isdigit():
        try:
          matched_player = Player.objects.get(pk=player_id)
          gold = decimal.Decimal(amount)
          old_gold = decimal.Decimal(0)
          # 取得原始的金幣/鑽石
          if jewel_type == "1":
            old_gold = matched_player.gold_total
          else:
            old_gold = matched_player.star
          # 新增系統補幣紀錄(AddValue)
          newAddValue = AddValue.objects.create(
              player_id = player_id, 
              type = addvalue_type,
              gold = int(amount),
              description = desc,
              admin_account = admin_account,
              old_gold = old_gold,
              jewel_type = jewel_type
          )
          if jewel_type == "1":
            # 新增玩家金流紀錄(PlayerGold)
            newPlayerGold = PlayerGold.objects.create(
                player_id = player_id, 
                type = addvalue_type,
                amount = gold,
                old_amount = old_gold
            )
            # 連動更新官方金流(GoldFlow) & GoldFlowSummary
            Helpers().goldFlowProcess(player_id, addvalue_type,gold,admin_account)
            # 更新玩家的金幣
            matched_player.gold_total += gold
          else:
            # 新增玩家鑽石紀錄(PlayerStar)
            newPlayerGold = PlayerStar.objects.create(
                player_id = player_id, 
                star_type = addvalue_type,
                obj_playerid = 99999999,
                star = gold,
                old_star = old_gold
            )            
            # 連動更新官方鑽石紀錄(StarFlow) & GoldFlowSummary
            Helpers().procCorpStar(player_id, addvalue_type, gold)
            # 更新玩家的鑽石
            matched_player.star += gold

          matched_player.last_modify_date = datetime.datetime.now()
          matched_player.save()
          new_gold = matched_player.gold_total
          new_star = matched_player.star

          ret_msg = "作業完成。"
        except Player.DoesNotExist:
          ret_msg = "玩家ID {} 不存在".format(player_id)
      else:
        ret_msg = "玩家ID {} 格式不正確".format(player_id)

    result = {
      'msg':ret_msg,
      'new_gold':format(int(new_gold),','),
      'new_star':format(new_star,'0,.2f')
      }
    # print(f"[addvalue]result:{result}")

    if request.is_ajax():
      return JsonResponse(result, safe=False)

  return render(request, "member/player.html", result,)

# 玩家資訊-VIP組織圖
def vip(request):
  # print("[vip]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')
  
  player_id = request.GET.get("player_id",'0')
  vip_type = request.GET.get("vip_type",'0')

  result = Helpers().getVIPResult(int(vip_type), int(player_id), 0)
  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/vip.html", result,)

# 玩家資訊-用seat取得VIP組織圖
def vipseat(request):
  # print("[vipseat]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  player_id = request.GET.get("player_id",'0')
  vip_type = request.GET.get("vip_type",'0')
  seat = request.GET.get("seat",'0')

  result = Helpers().getVIPResult(int(vip_type), int(player_id), int(seat))

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/vip.html", result,)

'''
  遊戲資訊-牌局紀錄
'''
def game_room(request):
  # print("[game_room]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  room = request.GET.get("room",None)
  start_date = request.GET.get("startTime1",None)
  end_date = request.GET.get("endTime1",None)

  # print(f"[game_room]room:{room} start_date:{start_date} end_date:{end_date}")

  data = []
  filters = Q()
  filters.connector = "AND"
  if room is not None and len(room) > 0:
    filters.children.append(("room",room))

  if start_date is not None and len(start_date) > 0:
    date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[game_room]2.start_date:{date1} ")
    filters.children.append(("created_date__gte",date1))

  if end_date is not None and len(end_date) > 0:
    date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[game_room]3.end_date:{date1}")
    filters.children.append(("created_date__lte",date1))
    
  ret1 = GameRoom.objects.filter(filters).order_by('id')

  for d in ret1:
    rs = {}
    rs['id'] = d.id
    rs['room'] = d.room
    area = "{}({}/{})".format(d.get_area_display(),d.base,d.points)
    rs['area'] = area
    rs['created_date'] = datetime.datetime.strftime(d.created_date, "%Y-%m-%d %H:%M:%S")
    rs['detail'] = d.room
    rs['state'] = d.get_state_display()
    rs['total_commission'] = d.total_commission

    data.append(rs)

  # print(f"[game_room]data:{data}")

  result = {
    "rs1": data,
  }

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/game_room.html", result,)

# 遊戲資訊-牌局紀錄-詳細
def gameroom_detail(request):
  # print("[gameroom_detail]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')
  
  room_id = request.GET.get("room_id",None)

  # print(f"[gameroom_detail]1.room_id:{room_id}")

  game_time = ""
  game_room = ""
  room_state = ""
  player1 = 0
  player2 = 0
  player3 = 0
  player4 = 0
  # 紀錄玩家總成績
  player1_score = 0
  player2_score = 0
  player3_score = 0
  player4_score = 0

  # 紀錄玩家總金流異動
  player1_s_flow = 0
  player2_s_flow = 0
  player3_s_flow = 0
  player4_s_flow = 0
  player1_e_flow = 0
  player2_e_flow = 0
  player3_e_flow = 0
  player4_e_flow = 0

  player1_flow = 0
  player2_flow = 0
  player3_flow = 0
  player4_flow = 0
  # 官方抽水
  player1_corp_bonus = decimal.Decimal("0")
  player2_corp_bonus = decimal.Decimal("0")
  player3_corp_bonus = decimal.Decimal("0")
  player4_corp_bonus = decimal.Decimal("0")
  all_corp_bonus = decimal.Decimal("0")

  result = {}
  data1 = []
  summary = []
  bonus = []
  msg = ""
  status = 0
  if room_id is not None and len(room_id) > 0:
    try:
      matchRoom = GameRoom.objects.get(pk=room_id)
      game_time = ''
      if matchRoom.start_date == None:
        game_time = ''
      else:
        game_time = datetime.datetime.strftime(matchRoom.start_date, "%Y-%m-%d %H:%M:%S")
      game_room = matchRoom.room
      room_state = matchRoom.get_state_display()
      # 取 GameRun 資料
      ret_cnt = GameRun.objects.filter(game_room_id = room_id).count()
      if ret_cnt > 0:
        status = 1
        ret1 = GameRun.objects.filter(game_room_id = room_id).order_by("seqno_start_date")

        seqno = 2
        for d1 in ret1:
          player1 = d1.player1
          player2 = d1.player2
          player3 = d1.player3
          player4 = d1.player4

          rs1 = {}
          rs1['seqno'] = seqno
          rs1['id'] = d1.run_id
          start_time = ''
          if d1.seqno_start_date == None:
            start_time = ''
          else:
            start_time = '({})'.format(datetime.datetime.strftime(d1.seqno_start_date, "%Y-%m-%d %H:%M:%S"))
            
          rs1['start_time'] = start_time
          desc = '{}.{}'.format(d1.seqno,d1.run_name)
          rs1['desc'] = desc
          # first player
          rs1['player1_win_str'] = format(d1.player1_win,'0,.2f')
          gold1 = format(int(d1.player1_start_gold),',')
          if d1.player1_win > 0:
            player1_e_flow = int(d1.player1_start_gold+d1.player1_win-d1.total_bonus)
            win_lost = d1.player1_win - d1.total_bonus 
          else:
            player1_e_flow = int(d1.player1_start_gold+d1.player1_win)
            win_lost = d1.player1_win
            
          gold2 = format(player1_e_flow,',')
          rs1['player1_gold_flow'] = '({} ⟶ {}：'.format(gold1,gold2)
          rs1['player1_win_lost'] = format(win_lost,'0,.2f')

          # second player
          rs1['player2_win_str'] = format(d1.player2_win,'0,.2f')
          gold1 = format(int(d1.player2_start_gold),',')
          if d1.player2_win > 0:
            player2_e_flow = format(int(d1.player2_start_gold+d1.player2_win-d1.total_bonus))
            win_lost = d1.player2_win - d1.total_bonus
          else:
            player2_e_flow = int(d1.player2_start_gold+d1.player2_win)
            win_lost = d1.player2_win

          gold2 = format(player2_e_flow,',')
          rs1['player2_gold_flow'] = '({} ⟶ {}：'.format(gold1,gold2)
          rs1['player2_win_lost'] = format(win_lost,'0,.2f')

          # third player
          rs1['player3_win_str'] = format(d1.player3_win,'0,.2f')
          gold1 = format(int(d1.player3_start_gold),',')
          if d1.player3_win > 0:
            player3_e_flow = int(d1.player3_start_gold+d1.player3_win-d1.total_bonus)
            win_lost = d1.player3_win - d1.total_bonus 
          else:
            player3_e_flow = int(d1.player3_start_gold+d1.player3_win)
            win_lost = d1.player3_win
            
          gold2 = format(player3_e_flow,',')
          rs1['player3_gold_flow'] = '({} ⟶ {}：'.format(gold1,gold2)
          rs1['player3_win_lost'] = format(win_lost,'0,.2f')

          # fourth player
          rs1['player4_win_str'] = format(d1.player4_win,'0,.2f')
          gold1 = format(int(d1.player4_start_gold),',')
          if d1.player4_win > 0:
            player4_e_flow = int(d1.player4_start_gold+d1.player4_win-d1.total_bonus)
            win_lost = d1.player4_win - d1.total_bonus 
          else:
            player4_e_flow = int(d1.player4_start_gold+d1.player4_win)
            win_lost = d1.player4_win

          gold2 = format(player4_e_flow,',')
          rs1['player4_gold_flow'] = '({} ⟶ {}：'.format(gold1,gold2)
          rs1['player4_win_lost'] = format(win_lost,'0,.2f')

          rs1['corp_bonus'] = Helpers().getShowDigits(d1.total_bonus)

          player1_score += int(d1.player1_win)
          player2_score += int(d1.player2_win)
          player3_score += int(d1.player3_win)
          player4_score += int(d1.player4_win)
          # 紀錄第一筆資料的起始金額
          if seqno == 2:
              player1_s_flow = int(d1.player1_start_gold)
              player2_s_flow = int(d1.player2_start_gold)
              player3_s_flow = int(d1.player3_start_gold)
              player4_s_flow = int(d1.player4_start_gold)

          player1_corp_bonus += d1.player1_corp_bonus
          player2_corp_bonus += d1.player2_corp_bonus
          player3_corp_bonus += d1.player3_corp_bonus
          player4_corp_bonus += d1.player4_corp_bonus

          data1.append(rs1)
          seqno = seqno + 1

        # 處理總分
        # 計算玩家金流異動
        player1_flow = player1_e_flow - player1_s_flow
        player2_flow = player2_e_flow - player2_s_flow
        player3_flow = player3_e_flow - player3_s_flow
        player4_flow = player4_e_flow - player4_s_flow
        rs2 = {}
        rs2['seqno'] = 1
        rs2['id'] = 'none'
        rs2['start_time'] = ''
        rs2['desc'] = '總分'
        # first player
        rs2['player1_win_str'] = format(player1_score,',')
        rs2['player1_gold_flow'] = ''
        rs2['player1_win_lost'] = format(player1_flow,',')

        # second player
        rs2['player2_win_str'] = format(player2_score,',')
        rs2['player2_gold_flow'] = ''
        rs2['player2_win_lost'] = format(player2_flow,',')

        # third player
        rs2['player3_win_str'] = format(player3_score,',')
        rs2['player3_gold_flow'] = ''
        rs2['player3_win_lost'] = format(player3_flow,',')

        # fourth player
        rs2['player4_win_str'] = format(player4_score,',')
        rs2['player4_gold_flow'] = ''
        rs2['player4_win_lost'] = format(player4_flow,',')

        rs2['corp_bonus'] = ''
        summary.append(rs2)

        # 處理抽水
        # 計算每個玩家的官方抽水金額
        rs3 = {}
        rs3['seqno'] = seqno
        rs3['id'] = 'none'
        rs3['start_time'] = ''
        rs3['desc'] = '抽水'
        # first player
        rs3['player1_win_str'] = Helpers().getShowDigits(format(player1_corp_bonus,'0,.7f'))
        rs3['player1_gold_flow'] = ''
        rs3['player1_win_lost'] = player1_corp_bonus

        # second player
        rs3['player2_win_str'] = Helpers().getShowDigits(format(player2_corp_bonus,'0,.7f'))
        rs3['player2_gold_flow'] = ''
        rs3['player2_win_lost'] = player2_corp_bonus

        # third player
        rs3['player3_win_str'] = Helpers().getShowDigits(format(player3_corp_bonus,'0,.7f'))
        rs3['player3_gold_flow'] = ''
        rs3['player3_win_lost'] = player3_corp_bonus
        
        # fourth player
        rs3['player4_win_str'] = Helpers().getShowDigits(format(player4_corp_bonus,'0,.7f'))
        rs3['player4_gold_flow'] = ''
        rs3['player4_win_lost'] = player4_corp_bonus

        # 官方總抽水金額
        all_corp_bonus = (player1_corp_bonus + player2_corp_bonus +
                          player3_corp_bonus + player4_corp_bonus)
        # 玩家代理抽水金額
        gold1 = Helpers().getShowDigits(format(all_corp_bonus,'0,.7f'))
        rs3['corp_bonus'] = '官方：{}'.format(gold1)

        bonus.append(rs3)

    except GameRoom.DoesNotExist:
        # print(f"[gameroom_detail]: GameRoom {player} not exist")
        pass

  player1_name = ""
  if player1 > 0:
     player1_name = Helpers().get_player_ref_name(player1)
  
  player2_name = ""
  if player2 > 0:
    player2_name = Helpers().get_player_ref_name(player2)
  
  player3_name = ""
  if player3 > 0:
    player3_name = Helpers().get_player_ref_name(player3)
  
  player4_name = ""
  if player4 > 0:
    player4_name = Helpers().get_player_ref_name(player4)

  if status == 1:
    result = {
      "status":1,
      "game_room": game_room,
      "game_time": game_time,
      "room_state": room_state,
      "player1_name": player1_name,
      "player2_name": player2_name,
      "player3_name": player3_name,
      "player4_name": player4_name,
      "rs1": data1,
      "summary": summary,
      "footer" : bonus
    }
  else:
    result = {
      "status":0,
      "game_room": game_room,
      "game_time": game_time,
      "room_state": room_state,
      "msg": "無場局紀錄"
    }    

  # if request.is_ajax():
  #   return JsonResponse(result, safe=False)

  return render(request, "member/gameroom_detail.html", result,)


# 遊戲資訊-玩家戰績
def show_score(request):
  # print("[show_score]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')
  
  player_name = ""
  result = {}
  today = datetime.date.today()

  if request.is_ajax():
    player = request.GET.get("player",None)
    
    data = []
    if player is not None and len(player) > 0 and player.isdigit():
      try:
        matched_player = Player.objects.get(pk=player)
        player_name = "玩家：{}".format(matched_player.nick_name)
        # print(f"[show_score]{player_name}")

        # 計算玩家的戰績資料(今日、昨日、本週、上週、本月、上月)
        # 戰績種類(score_type)：
        # 1 : 遊玩次數
        # 2 : 勝場次數
        # 3 : 自摸次數
        # 4 : 胡牌次數
        # 5 : 放槍次數
        # 6 : 最高連莊次數
        # 7 : 底15遊戲場數
        # 8 : 底30遊戲場數
        # print(f"[show_score]playerid:{player}")

        rs = Helpers().get_player_scores(player,1)    # 遊玩次數
        #print(f"[show_score]rs:{rs}")
        data.append(rs)
        rs = Helpers().get_player_scores(player,2)    # 勝場次數
        #print(f"[show_score]rs:{rs}")
        data.append(rs)
        rs = Helpers().get_player_scores(player,3)    # 自摸次數
        #print(f"[show_score]rs:{rs}")
        data.append(rs)
        rs = Helpers().get_player_scores(player,4)    # 胡牌次數
        #print(f"[show_score]rs:{rs}")
        data.append(rs)
        rs = Helpers().get_player_scores(player,5)    # 放槍次數
        #print(f"[show_score]rs:{rs}")
        data.append(rs)
        rs = Helpers().get_player_scores(player,6)    # 最高連莊次數
        #print(f"[show_score]rs:{rs}")
        data.append(rs)
        rs = Helpers().get_player_scores(player,7)    # 底15遊戲場數
        #print(f"[show_score]rs:{rs}")
        data.append(rs)
        rs = Helpers().get_player_scores(player,8)    # 底30遊戲場數
        #print(f"[show_score]rs:{rs}")
        data.append(rs)

        # print(f"[show_score]data:{data}")

      except Player.DoesNotExist:
        # print(f"[show_score]: player {player} not exist")
        player_name = "玩家ID：{} 不存在。".format(player)

      result = {
        "rs1": data,
        "player":player, 
        "player_name": player_name,
        "today":today
      }
      # print(f"[show_score]: result: {result}")
      return JsonResponse(result, safe=False)
  # else:
  #   print(f"[show_score]:not ajax")

  result = {"today":today}
  
  return render(request, "member/score.html", result,)

# 遊戲資訊-玩家排行
def leaderboard(request):
  # print("[leaderboard]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  now = datetime.datetime.now()
  #今天
  today = now
  result = {}

  if request.is_ajax():
    # print("[leaderboard]from ajax")
    orderby1 = request.GET.get("orderby",None)
    base1 = request.GET.get("base",None)
    daterange1 = request.GET.get("daterange",None)

    # print(f"[leaderboard]1.orderby:{orderby1}, base:{base1}, daterange:{daterange1}")

    filters = Q()
    filters.connector = "AND"
    if base1 != "-1":
      filters.children.append(("base",base1))
    
    if daterange1 != "-1":
      date_start = today
      date_end = today
      if daterange1 == "1":      # 本日
        date_start = today.replace(hour=0,minute=0,second=0,microsecond=0)
        date_end = today.replace(hour=23,minute=59,second=59,microsecond=999999)

      elif daterange1 == "2":      # 昨日
        #昨天
        yesterday = now - timedelta(days=1)
        date_start = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)
        date_end = yesterday.replace(hour=23,minute=59,second=59,microsecond=999999)

      elif daterange1 == "3":      # 本週
        #本周第一天和最后一天(第一天是星期一，最後一天是星期日)
        this_week_start = now - timedelta(days=now.weekday())
        this_week_end = now + timedelta(days=6-now.weekday())
        date_start = this_week_start.replace(hour=0,minute=0,second=0,microsecond=0)
        date_end = this_week_end.replace(hour=23,minute=59,second=59,microsecond=999999)

      elif daterange1 == "4":      # 上週
        #上周第一天和最后一天
        last_week_start = now - timedelta(days=now.weekday()+7)
        last_week_end = now - timedelta(days=now.weekday()+1)
        date_start = last_week_start.replace(hour=0,minute=0,second=0,microsecond=0)
        date_end = last_week_end.replace(hour=23,minute=59,second=59,microsecond=999999)

      elif daterange1 == "5":      # 本月
        #本月第一天和最后一天
        this_month_start = datetime.datetime(now.year, now.month, 1)
        if now.month == 12:
          this_month_end = datetime.datetime(now.year+1, 1, 1) - timedelta(days=1)
        else:
          this_month_end = datetime.datetime(now.year, now.month + 1, 1) - timedelta(days=1)
          
        date_start = this_month_start.replace(hour=0,minute=0,second=0,microsecond=0)
        date_end = this_month_end.replace(hour=23,minute=59,second=59,microsecond=999999)

      elif daterange1 == "6":      # 上月
        #上月第一天和最后一天
        this_month_start = datetime.datetime(now.year, now.month, 1)
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
        date_start = last_month_start.replace(hour=0,minute=0,second=0,microsecond=0)
        date_end = last_month_end.replace(hour=23,minute=59,second=59,microsecond=999999)
      
      # print(f"[leaderboard]date_start:{date_start}, date_end:{date_end}")

      filters.children.append(("created_date__gte",date_start))
      filters.children.append(("created_date__lte",date_end))

    qtype = Q()
    if orderby1 == "2":         # 勝場次數
        qtype.connector = "OR"
    else:
        qtype.connector = "AND"

    if orderby1 == "2":         # 勝場次數
        qtype.children.append(("win",1))
        qtype.children.append(("win_self_hand",1))
    elif orderby1 == "3":       # 自摸次數
        qtype.children.append(("win_self_hand",1))
    elif orderby1 == "4":       # 胡牌次數
        qtype.children.append(("win",1))
    elif orderby1 == "5":       # 放槍次數
        qtype.children.append(("lost_won",1))
    elif orderby1 == "6":       # 最高連莊次數
        qtype.children.append(("base",15))

    if orderby1 == "1":       # 遊玩次數
      ret1 = PlayerRoundResult.objects.filter(filters).annotate(count=Count('player')
             ).values('player','player__nick_name','player__gold_total',
                      'player__score', 'count').order_by('-count','player')
      # print(f"[leaderboard]ret1:{ret1}")
    elif orderby1 in("2","3","4","5"):     
      ret1 = PlayerRoundResult.objects.filter(filters).filter(qtype).annotate(count=Count('player')
             ).values('player','player__nick_name','player__gold_total',
                      'player__score', 'count').order_by('-count','player')
      # print(f"[leaderboard]ret1:{ret1}")
    elif orderby1 == "6":       # 最高連莊次數
      ret1 = PlayerGameRoom.objects.filter(filters).annotate(count=Max('banker_count')
             ).values('player','player__nick_name','player__gold_total',
                      'player__score', 'count').order_by('-count','player')
      # print(f"[leaderboard]ret1:{ret1}")

    data = []
    i = 1
    # print(ret1)
    for d in ret1:
      rs = {}
      rs['rank'] = i
      rs['playerName'] = d['player__nick_name']
      rs['playerID'] = d['player']
      rs['gold'] = format(d['player__gold_total'],'0,.2f')
      rs['score'] = format(d['player__score'],',')
      rs['playCount'] = d['count']

      data.append(rs)
      i = i + 1

    # print(f"[leaderboard]data:{data}")

    result = {
      "rs1": data,
      "today": today,
    }
    return JsonResponse(result, safe=False)

  
  result = {"today":today}

  return render(request, "member/leaderboard.html", result,)

'''
  公告管理
'''
class BulletinView(View):

  # @xframe_options_exempt
  def get(self, request):
    return render(request, "member/bulletin.html", )

# 發送公告
def sendmail(request):
  # print("[sendmail]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  operator = request.session.get('user_id','')
  receiver = request.POST.get("receiver",'')
  receiver_list = request.POST.get("receiver_list",'')
  subject = request.POST.get("subject",'')
  message = request.POST.get("message",'')

  list1 = []
  # print(f"[sendmail]receiver_list:{receiver_list}")
  if receiver == '2': # all player
    ret1 = Player.objects.all()
    for data in ret1:
      player_id = data.id
      email = data.email
      if email:
        one_receiver = {}
        one_receiver['player_id'] = player_id
        one_receiver['email'] = email
        list1.append(one_receiver)
        # print(f"[sendmail]one_receiver:{one_receiver}")
  else:
    send_list = receiver_list.split(',')
    # print(f"[sendmail]send_list:{send_list}")
    for i in range(0, len(send_list)):
      player_id = send_list[i]
      # print(f"[sendmail]player_id:{player_id}")
      try:
        matched = Player.objects.get(pk=player_id)
        player_id = matched.id
        email = matched.email
        if email:
          one_receiver = {}
          one_receiver['player_id'] = player_id
          one_receiver['email'] = email
          list1.append(one_receiver)
          # print(f"[sendmail]one_receiver:{one_receiver}")

      except Player.DoesNotExist:  
        continue

  if subject and message and len(list1) > 0:
    msg = Bulletin()
    msg.subject = subject
    msg.message = message
    msg.operator = operator
    msg.save()
    bulletin_id = msg.id
    # print(f"[sendmail]bulletin_id:{bulletin_id}")
    send_list = ""
    for j in range(0, len(list1)):
      one_email = list1[j]
      player_id = one_email['player_id']
      email = one_email['email']
      msg_recv = BulletinReceiver()
      msg_recv.player_id = player_id
      msg_recv.bulletin_id = bulletin_id
      msg_recv.email = email
      msg_recv.save()
      if send_list == "":
        send_list = "['{}'".format(email)
      else:
        send_list = "{},'{}'".format(send_list,email)
      send_list = "{}]".format(send_list)
      # print(f"[sendmail]send_list:{send_list}")

    # send mail
    # send_mail(subject, message, from_email, send_list)

  result = {"send_mail_count": len(send_list)}

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/bulletin.html", result)

'''
  公司報表相關專區-封鎖清單
'''
def block_list(request):
  # print("[block_list]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  result = {}
  ret1 = Player.objects.filter(is_lock=True)

  serializer = newBlockListSerializer(ret1, many=True)
  # print(f"[block_list]rs:{serializer.data}")

  result = {
    "rs1": serializer.data
  }

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/reports.html", result,)

'''
  管理員資訊-管理員清單
'''
def admin_list(request):
  # print("[admin_list]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')
    
  user_id = request.session.get('user_id',None)
  user_level = request.session.get('user_level',None)
  args = request.GET.get("args",None)

  result = {}
  # 系統主管人數
  sys_boss_count = Account.objects.filter(level='8',is_delete=False).count()
  # if sys_boss_count is None:
  #   sys_boss_count = 0
  # 客服主管人數
  rep_boss_count = Account.objects.filter(level='3',is_delete=False).count()
  # if rep_boss_count is None:
  #   rep_boss_count = 0
  # 一般客服人數
  rep_count = Account.objects.filter(level='2',is_delete=False).count()
  # if rep_count is None:
  #   rep_count = 0
  # print(f"[admin_list]sys_boss_count:{sys_boss_count}, rep_boss_count:{rep_boss_count}, rep_count:{rep_count}")

  if args is not None and len(args) > 0:
    if args.isdigit():
      ret1 = Account.objects.filter(is_delete=False).filter(Q(pk = args) | Q(phone_number = args) | Q(user_name = args))
    else:
      ret1 = Account.objects.filter(is_delete=False).filter(Q(phone_number = args) | Q(user_name = args))

  else:
    ret1 = Account.objects.filter(is_delete=False)

  # print(f"[admin_list]ret1 count:{ret1.count()}")
  data = []
  for d in ret1:
    rs = {}
    rs['id'] = d.id
    rs['user_account'] = d.user_account
    rs['user_password'] = d.user_password
    rs['user_name'] = d.user_name
    rs['phone_number'] = d.phone_number
    if d.last_login_date is not None:
      rs['last_login_date'] = datetime.datetime.strftime(d.last_login_date, "%Y-%m-%d %H:%M:%S")
    else:
      rs['last_login_date'] = ''

    rs['level'] = d.level
    rs['level_name'] = d.get_level_display()
    if rs['level'] < user_level:
      rs['action'] = 'Y'
    else:
      rs['action'] = 'N'

    data.append(rs)

  # print(f"[admin_list]data:{data}")
  result = {
    "rs1": data,
    "sys_boss_count": sys_boss_count,
    "rep_boss_count": rep_boss_count,
    "rep_count": rep_count
  }

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/admin_list.html", result,)

# 新增/更新管理員帳號
def account(request):
  # print("[account]")
  if not request.session.get('is_login',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/login/')

  if request.method == 'POST':
    user_id = request.session.get('uid',None)
    modify_user = request.session.get('user_id',None)

    # print(f"[account]request data:{request.POST}")

    action = request.POST.get('action')
    # print(f"[account]action:{action}")
    user_account = request.POST.get('user_account')
    level = request.POST.get('level')
    player_id = request.POST.get('player_id')
    # 系統身份(level)為代理玩家則代理玩家的ID不得為空
    if level == '1':
      if player_id is None:
        ret_msg = "帳號 {} 身份為代理玩家，其代理玩家ID不得為空。".format(user_account)
        #return Response("帳號 ‘%s' 身份為代理玩家，其代理玩家ID不得為空．" % useraccount, status=status.HTTP_400_BAD_REQUEST)
      else:
        if Helpers().checkAgentPlayer(player_id) == False:
          ret_msg = "代理玩家ID {}  不存在。".format(player_id)
          #return Response("代理玩家ID '%s' 不存在．" % playerid, status=status.HTTP_400_BAD_REQUEST)

    # Check 異動者的帳號是否存在
    if Account.objects.filter(user_account=modify_user).count() == 0:
      ret_msg = "異動者的帳號 {} 不存在".format(modify_user)
      #return Response("異動者的帳號 ‘%s' 不存在．" % modify_user, status=status.HTTP_400_BAD_REQUEST)

    uid = request.POST['uid']
    user_password = request.POST['user_password']
    user_name = request.POST['user_name']
    phone_number = request.POST['phone_number']
    user_account = request.POST['user_account']
    # 若為新增帳號，Check existing account (帳號名稱不能重複)
    if action == 'C':     # create a new account
      if Account.objects.filter(user_account=user_account).count() != 0:
        ret_msg = "帳號 {} 已經存在。".format(user_account)
        # print(f"[account]error:{ret_msg}")
        #return Response("帳號 ‘%s' 已經存在．" % user_account, status=status.HTTP_400_BAD_REQUEST)
      else:
        new_account = Account()
        new_account.user_account = user_account
        new_account.user_password = user_password
        new_account.user_name = user_name
        new_account.phone_number = phone_number
        new_account.level = level
        new_account.create_user = modify_user
        new_account.modify_user = modify_user
        new_account.save()
        datetime1 = new_account.created_date
        new_account.last_modify_date = datetime1
        new_account.save()
        
        ret_msg = "新增成功。"
        # print(f"[account]error:{ret_msg}")
    else:
      # 若為更新帳號，check pk is exist or not
      if uid is None:
        ret_msg = "The account pk value isn't exist!"
        # print(f"[account]error:{ret_msg}")
        #return Response(ret_msg, status=status.HTTP_400_BAD_REQUEST)
      else:

        try:
          match_account = Account.objects.get(pk=uid)
          match_account.user_name = user_name
          match_account.phone_number = phone_number
          match_account.level = level
          match_account.player_id = player_id
          match_account.modify_user = modify_user
          match_account.last_modify_date = datetime.datetime.now()
          match_account.save()

          ret_msg = "更新成功。"
          # print(f"[account]error:{ret_msg}")
        except Account.DoesNotExist:
          ret_msg = "管理員資料不存在。"
          # print(f"[account]error:{ret_msg}")
          #return Response("管理員資料不存在。", status=status.HTTP_400_BAD_REQUEST)

    result = {'msg':ret_msg}
  
    if request.is_ajax():
      return JsonResponse(result, safe=False)

  return render(request, "member/admin_list.html", result,)

# 刪除管理員
class DeleteAccountView(APIView):
  permission_classes = (IsAuthenticated,)

  def post(self, request, format=None):
    pk = request.POST.get("pk",None)
    modify_user = request.session.get('user_id',None)
    # print(f"pk:{pk}, modify_user:{modify_user}")
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
      return Response("管理員資料不存在。", status=status.HTTP_400_BAD_REQUEST)

# 管理員資訊-修改密碼
def password_change(request):
  # clear messages data
  storage = messages.get_messages(request)
  storage.used = True

  if request.method == 'POST':
    user_id = request.session.get('uid',None)
    modify_user = request.session.get('user_name',None)

    form = PasswordChangeForm(request.POST)
    if form.is_valid(): # 驗證表單
      old_pwd = form.cleaned_data['old_password']
      new_pwd = form.cleaned_data['new_password1']
      try:
        match_account = Account.objects.get(pk=user_id)
        useraccount = match_account.user_account
        account_pwd = match_account.user_password
        # print("old password1:"+account_pwd)

        if old_pwd != account_pwd:
          messages.error(request, form.error_messages['password_incorrect'])
        else:
          match_account.user_password = new_pwd
          match_account.modify_user = user_id
          match_account.last_modify_date = datetime.datetime.now()
          match_account.save()
          # 新增密碼修改記錄
          createdObj = Helpers().addChangePWDData(useraccount, old_pwd, new_pwd, modify_user)
          messages.success(request, '密碼修改成功。')

      except Account.DoesNotExist:
        err_msg = f("無此管理員 {user_id} 資料。")
        messages.error(request, err_msg)

  form = PasswordChangeForm(request.POST)
  return render(request,"member/password_change.html", locals())

'''
  登入
'''
def login(request):
  # print(request.method)
  d1=datetime.datetime.now()
  msg = f"[login]1-start ============================================"
  logger2.warning(msg)
  if request.session.get('is_login',None): # 檢查 session 確定是否登入，不允許重複登入
    return redirect("/")
    # return render(request,"member/index.html", ) # 若已登入則導向主頁

  if request.method == 'POST':  # 接收 POST 訊息，若無則讓返回空表單
    # for key, value in request.POST.items():
    #   print(f'Key: {key}')
    #   print(f'Value: {value}')
    d2=datetime.datetime.now()
    diff = (d2 - d1).total_seconds()
    msg = f"[login]2-start(post),spent : {diff} seconds"
    logger2.warning(msg)    
    login_form = LoginForm(request.POST)  # 導入表單類型
    d3=datetime.datetime.now()
    diff = (d3 - d2).total_seconds()
    msg = f"[login]3-loginForm導入,spent : {diff} seconds"
    logger2.warning(msg)    

    if login_form.is_valid(): # 驗證表單
      d4=datetime.datetime.now()
      diff = (d4 - d3).total_seconds()
      msg = f"[login]4-loginForm驗證表單,spent : {diff} seconds"
      logger2.warning(msg) 
      user_id  = login_form.cleaned_data['user_id']
      user_pwd = login_form.cleaned_data['user_pwd']
      login_system = login_form.cleaned_data['login_system']

      # print(f"user_id: {user_id}")
      # print(f"user_pwd: {user_pwd}")
      # print(f"login_system: {login_system}")

      if login_system != '1' and login_system != '2' :
        message = "系統代碼錯誤！"
        return render(request,"member/login1.html", locals())

      try:
        user = Account.objects.get(user_account=user_id)
        # print(f"is_delete: {user.is_delete}")
        # print(f"level: {user.level}")
        # print(f"user_password: {user.user_password}")
        d5=datetime.datetime.now()
        diff = (d5 - d4).total_seconds()
        msg = f"[login]5-get data,spent : {diff} seconds"
        logger2.warning(msg)
        if user.is_delete:
          message = f"帳號 {user.user_account} 無登入權限！"
          # print(message)
          return render(request,"member/login1.html", locals())

        if login_system == '1' and user.level == '2':
          message = f"帳號 {user.user_account} 無後台系統登入權限！"
          # print(message)
          return render(request,"member/login1.html", locals())

        if user.user_password != user_pwd :
          message = f"帳號 {user.user_account} 密碼錯誤！"
          # print(message)
          return render(request,"member/login1.html", locals())

        # print("驗證完成")
        # 使用 session 寫入登入資料
        request.session['is_login'] = True
        request.session['uid'] = user.id
        request.session['user_id'] = user.user_account
        request.session['user_name'] = user.user_name
        request.session['user_level'] = user.level
        request.session['player_id'] = user.player_id

        # 新增登入記錄
        # print(f"userid:{user.id}")
        # print(f"user.login_system:{user.level}")
        d6=datetime.datetime.now()
        diff = (d6 - d5).total_seconds()
        msg = f"[login]6-write data into session,spent : {diff} seconds"
        logger2.warning(msg)
        # print("新增登入記錄～")
        createdObj = Helpers().addLoginData(user.id, user.level)
        d7=datetime.datetime.now()
        diff = (d7 - d6).total_seconds()
        msg = f"[login]7-新增登入記錄,spent : {diff} seconds"
        logger2.warning(msg)
        last_login_date = createdObj.login_date
        user.last_login_date = last_login_date
        user.save()
        d8=datetime.datetime.now()
        diff = (d8 - d7).total_seconds()
        msg = f"[login]done,spent : {diff} seconds"
        logger2.warning(msg)
        message = "登入成功～"
        # print("登入成功～")
        return render(request, "member/index.html", )

      except:
        message = f"無此帳號( {user_id} )資料！"
        # print(f"{user_id} doesn't exist!")
        # print(message)

  login_form = LoginForm(request.POST)  # 返回空表單
  d9=datetime.datetime.now()
  diff = (d9 - d1).total_seconds()
  msg = f"[login]返回空表單,spent : {diff} seconds"
  logger2.warning(msg)
  return render(request,"member/login1.html", locals())

'''
  登出
'''
def logout(request):
  if not request.session.get('is_login',None): # 若尚未登入，就不需要登出
    return redirect('/member/login/')

  # print(f"Already login")
  request.session.flush()   # 將 session 內容清除
  # login_form = LoginForm(request.POST)
  # return render(request,"member/login1.html", locals())
  return redirect('/member/login/')

# 玩家後台系統專用 start --------------------------------------------------
'''
  登入
'''
# @xframe_options_exempt
def playerlogin(request):
  if request.session.get('is_playerlogin',None): # 檢查 session 確定是否登入，不允許重複登入
    return redirect("/")

  d1=datetime.datetime.now()
  msg = f"[playerlogin]1-start ============================================"
  logger2.warning(msg)
  if request.method == 'POST':  # 接收 POST 訊息，若無則讓返回空表單
    login_form = LoginForm2(request.POST)  # 導入表單類型
    d2=datetime.datetime.now()
    diff = (d2 - d1).total_seconds()
    msg = f"[playerlogin]2-loginForm2導入,spent : {diff} seconds"
    logger2.warning(msg)
    if login_form.is_valid(): # 驗證表單
      d3=datetime.datetime.now()
      diff = (d3 - d2).total_seconds()
      msg = f"[playerlogin]3-loginForm2驗證表單,spent : {diff} seconds"
      logger2.warning(msg)

      user_id  = login_form.cleaned_data['user_id']
      user_pwd = login_form.cleaned_data['user_pwd']
      login_system = login_form.cleaned_data['login_system']
      # print(f'[playerlogin]user_id:{user_id}, login_system:{login_system}')
      if login_system != '3' :
        message = "系統代碼錯誤！"
        return render(request,"member/playerlogin.html", locals())

      try:
        player = Player.objects.get(id=user_id)
        d4=datetime.datetime.now()
        diff = (d4 - d3).total_seconds()
        msg = f"[playerlogin]5-get data,spent : {diff} seconds"
        logger2.warning(msg)
        if player.is_lock:
          message = f"帳號 {player.nick_name} 無登入權限！"
          # print(message)
          return render(request,"member/playerlogin.html", locals())

        if login_system != '3':
          message = f"帳號 {player.id} 無後台系統登入權限！"
          # print(message)
          return render(request,"member/playerlogin.html", locals())

        # 連線到game server去確認帳號及密碼
        if not user_view.objects.filter(pid=user_id).exists():
          message = f"{player.id} 為非合法的帳號！"
          return render(request,"member/playerlogin.html", locals())

        gameplayer = user_view.objects.get(pid=user_id)
        if user_pwd != gameplayer.password:
          message = f"{player.id} 密碼錯誤！"
          return render(request,"member/playerlogin.html", locals())

        # print("驗證完成")
        # 使用 session 寫入登入資料
        request.session['is_playerlogin'] = True
        request.session['uid'] = player.id
        request.session['user_id'] = player.id
        request.session['user_name'] = player.nick_name
        d5=datetime.datetime.now()
        diff = (d5 - d4).total_seconds()
        msg = f"[playerlogin]5-write data into session,spent : {diff} seconds"
        logger2.warning(msg)
        # print("新增登入記錄～")
        createdObj = Helpers().addPlayerLoginData(player.id)
        d6=datetime.datetime.now()
        diff = (d6 - d5).total_seconds()
        msg = f"[playerlogin]6-新增登入記錄,spent : {diff} seconds"
        logger2.warning(msg)

        user_id = request.session.get('user_id',0)
        user_name = request.session.get('user_name','')
        d7=datetime.datetime.now()
        diff = (d7 - d6).total_seconds()
        msg = f"[playerlogin]7-done,spent : {diff} seconds"
        logger2.warning(msg)
        message = "登入成功～"
        return render(request, "member/playerindex.html", locals())

      except Player.DoesNotExist:
        message = f"無此帳號( {user_id} )資料！"
        # print(message)

  login_form = LoginForm2(request.POST)  # 返回空表單
  d8=datetime.datetime.now()
  diff = (d8 - d1).total_seconds()
  msg = f"[playerlogin]返回空表單,spent : {diff} seconds"
  logger2.warning(msg)
  return render(request,"member/playerlogin.html", locals())

'''
  登出
'''
# @xframe_options_exempt
def playerlogout(request):
  if not request.session.get('is_playerlogin',None): # 若尚未登入，就不需要登出
    return redirect('/member/playerlogin/')

  # print(f"Already login")
  request.session.flush()   # 將 session 內容清除
  return redirect('/member/playerlogin/')

'''
  首頁
'''
# @xframe_options_exempt
def playerindex(request):
  # print("call playerindex~")
  if not request.session.get('is_playerlogin',None):
    # print("玩家尚未登入")
    # 重新登入
    return redirect('/member/playerlogin/')

  user_id = request.session.get('user_id',0)
  user_name = request.session.get('user_name','')
  
  return render(request, "member/playerindex.html", locals())

# 玩家後台系統-玩家資訊
# @xframe_options_exempt
def player1(request):
  # print("[player1]")
  if not request.session.get('is_playerlogin',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/playerlogin/')

  # 檢查 session 的user_id是否為數字(玩家都用玩家ＩＤ登入)
  checkLoginId(request)

  user_id = player_id = request.session.get('user_id',0)
  user_name = request.session.get('user_name','')  
  # print(f"[player1]user_id:{user_id}, user_name:{user_name}")

  start_date = request.GET.get("startTime1",None)
  end_date = request.GET.get("endTime1",None)

  # print(f"[player1]1.start_date:{start_date} end_date:{end_date}")

  result = {}

  # 個人資訊
  ret = Player.objects.get(pk = user_id)
  rs = {}
  rs['id'] = ret.id
  rs['nick_name'] = ret.nick_name
  rs['gold'] = format(ret.gold_total,'0,.2f')
  rs['star'] = format(ret.star,'0,.2f')
  rs['phone_number'] = ret.phone_number
  rs['register_mac_addr'] = ret.register_mac_addr
  rs['bind_playerid'] = ret.bind_player
  rs['bind_playername'] = ret.get_bind_player_name()
  if ret.line_id is None:
    rs['line_id'] = ''
  else:  
    rs['line_id'] = ret.line_id  

  # 計算歷史場數
  qc = Q()
  qc.connector = "AND"
  qc.children.append(("player_id",ret.id))
  history_game_runs = PlayerRoundResult.objects.filter(qc).count()
  rs['history_game_runs'] = history_game_runs
  rs['score'] = ret.score
  if ret.last_login_date is not None:
    rs['last_login_date'] = datetime.datetime.strftime(ret.last_login_date, "%Y-%m-%d %H:%M:%S")
  else:
    rs['last_login_date'] = ''

  rs['created_date'] = datetime.datetime.strftime(ret.created_date, "%Y-%m-%d %H:%M:%S")
  rs['player_type'] = ret.permission_type
  rs['permission_type'] = ret.get_permission_type_display()
  if ret.is_lock:
    rs['state'] = "1"
  else:
    rs['state'] = "0"

  filters = Q()
  filters.connector = "AND"

  now = datetime.datetime.now()
  #今天
  today = now
  
  if start_date is not None and len(start_date) > 0:
    date1 = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[player1]2.start_date:{date1} ")
    filters.children.append(("created_date__gte",date1))
  else:  #  預設抓一天
    yesterday = now - timedelta(days=1)
    date1 = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)
    # print(f"[goldflow]2.start_date:{date1} ")
    filters.children.append(("created_date__gte",date1))

  if end_date is not None and len(end_date) > 0:
    date1 = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
    # print(f"[player1]3.end_date:{date1}")
    filters.children.append(("created_date__lte",date1))
  else:
    date1 = today.replace(hour=23,minute=59,second=59,microsecond=999999)
    # print(f"[goldflow]2.start_date:{date1} ")
    filters.children.append(("created_date__lte",date1))

  # 登入紀錄
  q1 = Q()
  q1.connector = "AND"
  q1.children.append(("type","1"))
  q1.children.append(("player_id",player_id))
  ret1 = IPInfo.objects.filter(filters).filter(q1).order_by("id")
  data1 = []
  for d1 in ret1:
    rs1 = {}
    rs1['id'] = d1.id
    rs1['login_ip'] = d1.ip
    rs1['created_date'] = datetime.datetime.strftime(d1.created_date, "%Y-%m-%d %H:%M:%S")

    data1.append(rs1)

  # 轉幣紀錄
  q2 = Q()
  q2.connector = "OR"
  q2.children.append(("sender_id",player_id))
  q2.children.append(("receiver_id",player_id))
  ret2 = TransferGold.objects.filter(filters).filter(q2).order_by("id")
  data2 = []
  for d2 in ret2:
    rs2 = {}
    rs2['id'] = d2.id
    rs2['jewel'] = d2.get_jewel_type_display()
    rs2['sender_id'] = d2.sender_id
    rs2['sender'] = Helpers().get_player_nickname(d2.sender_id)
    gold1 = format(d2.sender_gold,',')
    gold2 = format(d2.sender_gold+d2.amount,',')
    sender_gold = '${} ⟶ ${}'.format(gold1,gold2)
    rs2['sender_gold'] = sender_gold 
    rs2['receiver_id'] = d2.receiver_id
    rs2['receiver'] = Helpers().get_player_nickname(d2.receiver_id)
    gold1 = format(d2.receiver_gold,',')
    gold2 = format(d2.receiver_gold-d2.amount,',')
    receiver_gold = '${} ⟶ ${}'.format(gold1,gold2)
    rs2['receiver_gold'] = receiver_gold
    rs2['amount'] = format(d2.amount,',')
    rs2['created_date'] = datetime.datetime.strftime(d2.created_date, "%Y-%m-%d %H:%M:%S")

    data2.append(rs2)

  # 補幣紀錄
  q3 = Q()
  q3.connector = "AND"
  q3.children.append(("type","2"))
  q3.children.append(("player_id",player_id))
  ret3 = AddValue.objects.filter(filters).filter(q3).order_by("id")

  data3 = []
  for d3 in ret3:
    rs3 = {}
    rs3['id'] = d3.id
    rs3['jewel'] = d3.get_jewel_type_display()
    rs3['admin_account'] = d3.admin_account
    rs3['player'] = Helpers().get_player_nickname(d3.player_id)
    rs3['gold'] = format(d3.gold,',')
    rs3['description'] = d3.description
    rs3['created_date'] = datetime.datetime.strftime(d3.created_date, "%Y-%m-%d %H:%M:%S")

    data3.append(rs3)

  # 金流異動
  q4 = Q()
  q4.connector = "AND"
  q4.children.append(("player_id",player_id))
  ret4 = PlayerGold.objects.filter(filters).filter(q4).order_by("id")
  data4 = []
  for d4 in ret4:
    rs4 = {}
    rs4['id'] = d4.id
    tradetype = ""
    if d4.type == "12" or d4.type == "13":
      tradetype = "玩家轉幣"
    elif d4.type == "15":
      tradetype = "四人麻將({})".format(d4.run_id)
    else:
      tradetype = d4.get_type_display()
    rs4['tradetype'] = tradetype
    rs4['amount'] = format(d4.amount,'0,.6f')
    # 金流異動欄位
    gold1 = format(d4.old_amount,'0,.2f')
    gold2 = format(d4.old_amount+d4.amount,'0,.2f')
    goldflow = '${} ⟶ ${}'.format(gold1,gold2)
    rs4['goldflow'] = goldflow
    rs4['created_date'] = datetime.datetime.strftime(d4.created_date, "%Y-%m-%d %H:%M:%S")

    data4.append(rs4)

  q5 = Q()
  q5.connector = "OR"
  q5.children.append(("player1",player_id))
  q5.children.append(("player2",player_id))
  q5.children.append(("player3",player_id))
  q5.children.append(("player4",player_id))
  ret5 = GameRun.objects.filter(filters).filter(q5
                              ).values('run_id','base','game_room', 
                                       'game_room__room',
                                       'game_room__room_create_date', 
                                       'game_room__area', 
                                       'game_room__state',
                                       'game_room__points', 
                                       'game_room__total_commission')
  data5 = []
  for d5 in ret5:
    rs5 = {}
    rs5['run_id'] = d5['run_id']  # 遊戲局號(回播碼)，GameRun's pk
    rs5['gametype'] = d5['base']
    area_str = Helpers().get_gamerun_area(d5['run_id'])
    area = '{}({}/{})'.format(area_str,d5['base'],d5['game_room__points'])
    rs5['area'] = area
    state = Helpers().get_gamerun_state(d5['run_id'])
    rs5['state'] = state
    all_bonus = d5['game_room__total_commission']
    rs5['all_bonus'] = all_bonus
    rs5['created_date'] = datetime.datetime.strftime(d5['game_room__room_create_date'], "%Y-%m-%d %H:%M:%S")
    rs5['detail'] = d5['run_id']

    data5.append(rs5)

  # 鑽石紀錄
  ret6 = PlayerStar.objects.filter(filters).filter(q4).order_by("id")
  data6 = []
  for d6 in ret6:
    rs6 = {}
    rs6['id'] = d6.id
    rs6['star_type'] = d6.get_star_type_display()
    rs6['star'] = format(d6.star,',')
    # 鑽石異動欄位
    star1 = format(d6.old_star,'0,.2f')
    star2 = format(d6.old_star+d6.star,'0,.2f')
    starflow = '${} ⟶ ${}'.format(star1,star2)
    rs6['starflow'] = starflow    
    rs6['created_date'] = datetime.datetime.strftime(d6.created_date, "%Y-%m-%d %H:%M:%S")

    data6.append(rs6)

  # print(f"[player1]rs:{rs}")

  # print(f"[player1]data1:{data1}")
  # print(f"[player1]data2:{data2}")
  # print(f"[player1]data3:{data3}")
  # print(f"[player1]data4:{data4}")
  # print(f"[player1]data5:{data5}")
  # print(f"[player1]data6:{data6}")

  admin_account = request.session.get('user_id','')
  result = {
    "data": rs,
    "rs1": data1,
    "rs2": data2,
    "rs3": data3,
    "rs4": data4,
    "rs5": data5,
    "rs6": data6,
    "user_id":user_id,
    "user_name":user_name
  }

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/player1.html", result,)

# VIP組織圖
# @xframe_options_exempt
def playervip(request):
  # print("[playervip]1.")
  if not request.session.get('is_playerlogin',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/playerlogin/')

  # 檢查 session 的user_id是否為數字(玩家都用玩家ＩＤ登入)
  checkLoginId(request)

  user_id = player_id = request.session.get('user_id',0)
  user_name = request.session.get('user_name','')
  # print(f"[playervip]user_id:{user_id}, user_name:{user_name}")

  vip_type = request.GET.get("vip_type",0)
  result = {}
  if vip_type != 0:
    # print(f"[playervip]1.vip_type:{vip_type}, player_id:{player_id}")
    result = Helpers().getVIPResult(int(vip_type), int(player_id), 0)
    # print(f"[playervip]1.result:{result}")

  result['user_id'] = user_id
  result['user_name'] = user_name

  # print(f"[playervip]2.result:{result}")

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/playervip.html", result,)

# @xframe_options_exempt
def playervipseat(request):
  # print("[playervipseat]1.")
  if not request.session.get('is_playerlogin',None):
    # print("尚未登入")
    # 重新登入
    return redirect('/member/playerlogin/')
  
  # 檢查 session 的user_id是否為數字(玩家都用玩家ＩＤ登入)
  checkLoginId(request)

  user_id = player_id = request.session.get('user_id',0)
  user_name = request.session.get('user_name','')
  # print(f"[playervipseat]user_id:{user_id}, user_name:{user_name}")

  vip_type = request.GET.get("vip_type",0)
  seat = request.GET.get("seat",'0')
  
  result = {}
  if vip_type != 0:
    # print(f"[playervipseat]1.vip_type:{vip_type}, player_id:{player_id}, seat:{seat}")
    result = Helpers().getVIPResult(int(vip_type), int(player_id), int(seat))
    # print(f"[playervipseat]1.result:{result}")

  result['user_id'] = user_id
  result['user_name'] = user_name

  # print(f"[playervipseat]2.result:{result}")

  if request.is_ajax():
    return JsonResponse(result, safe=False)

  return render(request, "member/playervip.html", result,)

# 檢查 session 的user_id是否為數字(玩家都用玩家ＩＤ登入)
# @xframe_options_exempt
def checkLoginId(request):
  user_id = request.session.get('user_id',None)
  try:
    player_id = int(user_id)

  except:
    request.session.flush()   # 將 session 內容清除
    err_msg = f"非合法的玩家ID:{user_id}"
    logger2.warning(err_msg)
    messages.error(request, err_msg)
    return render(request,'/member/playerlogin.html', locals())

# 玩家後台系統專用 end ------------------------------------------------------