from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction,DatabaseError
import json
import time
from CMDB import settings 
from baseline import models
import base64
from django.views.decorators.csrf import csrf_exempt,csrf_protect
import baseline.linuxVulnScanUtil
import baseline.windowsVulnScanUtil
from pathlib import Path
import re
# Create your views here.
def middleware_check_res_display(request):
    scanTime=str(base64.urlsafe_b64decode(bytes(request.GET['scanTime'],encoding="utf-8")),encoding="utf-8")
    macaddr=str(base64.urlsafe_b64decode(bytes(request.GET['macaddr'],encoding="utf-8")),encoding="utf-8")
    middlewareCheckRes=models.MiddlewareCheckResMeta.objects.filter(scanTime=scanTime,macaddr=macaddr)
    middlewareCheckRes=middlewareCheckRes[0]
    middlewareCheckResStr=middlewareCheckRes.middlewareCheckResMeta
    middlewareCheckResDict=json.loads(middlewareCheckResStr)
    redis_check_res=middlewareCheckResDict['redis_check_res']
    nginx_check_res=middlewareCheckResDict['nginx_check_res']
    tomcat_check_res=middlewareCheckResDict['tomcat_check_res']
    apache_check_res=middlewareCheckResDict['apache_check_res']
    return render(request,'baseline/middleware_check_res_display.html',locals())
def vuln_check_res_display(request):
    scanTime=str(base64.urlsafe_b64decode(bytes(request.GET['scanTime'],encoding="utf-8")),encoding="utf-8")
    macaddr=str(base64.urlsafe_b64decode(bytes(request.GET['macaddr'],encoding="utf-8")),encoding="utf-8")
    osVersion=str(base64.urlsafe_b64decode(bytes(request.GET['osVersion'],encoding="utf-8")),encoding="utf-8")
    vulnCheckRes=models.VulnCheckRes.objects.filter(scanTime=scanTime,macaddr=macaddr)[0]
    vulnCheckResList=json.loads(vulnCheckRes.vulnCheckRes)
    if "Windows" in osVersion:
        return render(request,'baseline/windows_vuln_check_res_display.html',locals())
    else:
        return render(request,'baseline/linux_vuln_check_res_display.html',locals())
def check_choice(request):
    osVersion=str(base64.urlsafe_b64decode(bytes(request.GET['osVersion'],encoding="utf-8")),encoding="utf-8")
    scanTime=str(base64.urlsafe_b64decode(bytes(request.GET['scanTime'],encoding="utf-8")),encoding="utf-8")
    macaddr=str(base64.urlsafe_b64decode(bytes(request.GET['macaddr'],encoding="utf-8")),encoding="utf-8")
    scanType=str(base64.urlsafe_b64decode(bytes(request.GET['scanType'],encoding="utf-8")),encoding="utf-8")
    if scanType == "OS":
        if "Window" in osVersion:
            scanRes = models.WindowsScanRes.objects.filter(scanTime=scanTime,macaddr=macaddr)
            checkRes = models.WindowsCheckRes.objects.filter(scanTime=scanTime,macaddr=macaddr)
            if len(scanRes) ==0 or len(checkRes) == 0:
                return HttpResponse("0oops,something is wrong")
            scanRes=scanRes[0]
            checkRes=checkRes[0]
            # checkNum=len(checkRes.__dict__.keys()) - 6
            # passNum=0
            # for i in checkRes.__dict__.keys():
            #     if checkRes.__dict__[i] == "True":
            #         passNum = passNum + 1
            # failNum=checkNum - passNum - 1
            # checkScore=str(int(passNum/checkNum*100))
            return render(request,'baseline/check_choice_res_display.html',locals())
        else:
            scanRes = models.LinuxScanRes.objects.filter(scanTime=scanTime,macaddr=macaddr)
            checkRes = models.LinuxCheckRes.objects.filter(scanTime=scanTime,macaddr=macaddr)
            if len(scanRes) ==0 or len(checkRes) == 0:
                return HttpResponse("0oops,something is wrong")
            scanRes=scanRes[0]
            checkRes=checkRes[0]
            # checkNum=len(checkRes.__dict__.keys()) - 7
            # passNum=0
            # for i in checkRes.__dict__.keys():
            #     if checkRes.__dict__[i] == "True":
            #         passNum = passNum + 1
            # failNum=checkNum - passNum - 1
            # checkScore=str(int(passNum/checkNum*100))
            return render(request,'baseline/check_choice_res_display.html',locals())
def os_check_res_display(request):
    osVersion=str(base64.urlsafe_b64decode(bytes(request.GET['osVersion'],encoding="utf-8")),encoding="utf-8")
    scanTime=str(base64.urlsafe_b64decode(bytes(request.GET['scanTime'],encoding="utf-8")),encoding="utf-8")
    macaddr=str(base64.urlsafe_b64decode(bytes(request.GET['macaddr'],encoding="utf-8")),encoding="utf-8")
    scanType=str(base64.urlsafe_b64decode(bytes(request.GET['scanType'],encoding="utf-8")),encoding="utf-8")
    if scanType == "OS":
        if "Window" in osVersion:
            scanRes = models.WindowsScanRes.objects.filter(scanTime=scanTime,macaddr=macaddr)
            checkRes = models.WindowsCheckRes.objects.filter(scanTime=scanTime,macaddr=macaddr)
            if len(scanRes) ==0 or len(checkRes) == 0:
                return HttpResponse("0oops,something is wrong")
            scanRes=scanRes[0]
            checkRes=checkRes[0]
            checkNum=len(checkRes.__dict__.keys()) - 6
            passNum=0
            for i in checkRes.__dict__.keys():
                if checkRes.__dict__[i] == "True":
                    passNum = passNum + 1
            failNum=checkNum - passNum - 1
            checkScore=str(int(passNum/checkNum*100))
            return render(request,'baseline/windows_check_res_display.html',locals())
        else:
            scanRes = models.LinuxScanRes.objects.filter(scanTime=scanTime,macaddr=macaddr)
            checkRes = models.LinuxCheckRes.objects.filter(scanTime=scanTime,macaddr=macaddr)
            if len(scanRes) ==0 or len(checkRes) == 0:
                return HttpResponse("0oops,something is wrong")
            scanRes=scanRes[0]
            checkRes=checkRes[0]
            checkNum=len(checkRes.__dict__.keys()) - 7
            passNum=0
            for i in checkRes.__dict__.keys():
                if checkRes.__dict__[i] == "True":
                    passNum = passNum + 1
            failNum=checkNum - passNum - 1
            checkScore=str(int(passNum/checkNum*100))
            return render(request,'baseline/linux_check_res_display.html',locals())
def scan_res_display(request):
    scanResAll = models.AllScanResRecord.objects.all()
    return render(request,'baseline/scan_res_display.html',locals())
def windows_baseline_check(request):
    pass

def windows_vuln_check_res_store(data={}):
    KBResult=data
    windowsProductName = KBResult['basicInfo']['windowsProductName']
    windowsProductName = ((re.search("\w[\w|\s]+\d+[\s|$]",windowsProductName).group()).strip()).replace("Microsoft","").strip()
    windowsVersion = KBResult['basicInfo']['windowsVersion']
    print("系统信息如下:")
    print("{} {}".format(windowsProductName,windowsVersion))
    tmpKBList = KBResult['KBList']
    KBList = []
    for KB in tmpKBList:
        KBList.append(KB.replace("KB",""))
    print("KB信息如下:")
    print(KBList)
    print("EXP信息如下:")
    tmpList=baseline.windowsVulnScanUtil.select_CVE(tmpList=KBList,windowsProductName=windowsProductName,windowsVersion=windowsVersion)
    print(tmpList)
    return tmpList

@csrf_exempt
def windows_scan_res_report(request):
    if request.method == "POST":
        bodyData=request.body
        windowsScanResDict=json.loads(bodyData)
        basic_info=windowsScanResDict['basic_info']
        windowsVulnScanResDict=windowsScanResDict['vuln_scan_res']
        scanTime=basic_info['scanTime']
        osVersion=basic_info['osVersion']
        hostname=basic_info['hostname']
        macaddr=basic_info['macaddr']
        ipList=basic_info['ipList']
        account_check_res=windowsScanResDict['account_check_res']
        password_check_info=account_check_res['password_check_info']
        passwordHistorySize=password_check_info['passwordHistorySize']
        if int(passwordHistorySize) >= 5:
            ck_passwordHistorySize="True"
        else:
            ck_passwordHistorySize="False"
        maximumPasswordAge=password_check_info['maximumPasswordAge']
        if int(maximumPasswordAge) <= 90:
            ck_maximumPasswordAge="True"
        else:
            ck_maximumPasswordAge="False"
        minimumPasswordAge=password_check_info['minimumPasswordAge']
        if int(minimumPasswordAge) >= 1:
            ck_minimumPasswordAge="True"
        else:
            ck_minimumPasswordAge="False"
        passwordComplexity=password_check_info['passwordComplexity']
        if int(passwordComplexity) == 1:
            ck_passwordComplexity="True"
        else:
            ck_passwordComplexity="False"
        clearTextPassword=password_check_info['clearTextPassword']
        if int(clearTextPassword) == 1:
            ck_clearTextPassword="True"
        else:
            ck_clearTextPassword="False"
        minimumPasswordLength=password_check_info['minimumPasswordLength']
        if int(minimumPasswordLength) >= 8:
            ck_minimumPasswordLength="True"
        else:
            ck_minimumPasswordLength="False"
        account_lockout_info=account_check_res['account_lockout_info']
        lockoutDuration=account_lockout_info['lockoutDuration']
        if int(lockoutDuration) >= 15:
            ck_lockoutDuration="True"
        else:
            ck_lockoutDuration="False"
        lockoutBadCount=account_lockout_info['lockoutBadCount']
        if int(lockoutBadCount) <= 5:
            ck_lockoutBadCount="True"
        else:
            ck_lockoutBadCount="False"
        resetLockoutCount=account_lockout_info['resetLockoutCount']
        if int(resetLockoutCount) >=15 and int(resetLockoutCount) <= int(lockoutDuration):
            ck_resetLockoutCount="True"
        else:
            ck_resetLockoutCount="False"
        audit_check_res=windowsScanResDict['audit_check_res']
        auditPolicyChange=audit_check_res['auditPolicyChange']
        if int(auditPolicyChange) >= 1:
            ck_auditPolicyChange="True"
        else:
            ck_auditPolicyChange="False"
        auditLogonEvents=audit_check_res['auditLogonEvents']
        if int(auditLogonEvents) == 3:
            ck_auditLogonEvents="True"
        else:
            ck_auditLogonEvents="False"
        auditObjectAccess=audit_check_res['auditObjectAccess']
        if int(auditObjectAccess) >= 1:
            ck_auditObjectAccess="True"
        else:
            ck_auditObjectAccess="False"
        auditProcessTracking=audit_check_res['auditProcessTracking']
        if int(auditProcessTracking) == 3:
            ck_auditProcessTracking="True"
        else:
            ck_auditProcessTracking="False"
        auditDSAccess=audit_check_res['auditDSAccess']
        if int(auditDSAccess) == 3:
            ck_auditDSAccess="True"
        else:
            ck_auditDSAccess="False"
        auditSystemEvents=audit_check_res['auditSystemEvents']
        if int(auditSystemEvents) == 3:
            ck_auditSystemEvents="True"
        else:
            ck_auditSystemEvents="False"
        auditAccountLogon=audit_check_res['auditAccountLogon']
        if int(auditAccountLogon) == 3:
            ck_auditAccountLogon="True"
        else:
            ck_auditAccountLogon="False"
        auditAccountManage=audit_check_res['auditAccountManage']
        if int(auditAccountManage) == 3:
            ck_auditAccountManage="True"
        else:
            ck_auditAccountManage="False"
        userright_check_res=windowsScanResDict['userright_check_res']
        seTrustedCredManAccessPrivilegeIFNone=userright_check_res['seTrustedCredManAccessPrivilegeIFNone']
        if seTrustedCredManAccessPrivilegeIFNone == "True":
            ck_seTrustedCredManAccessPrivilegeIFNone="True"
        else:
            ck_seTrustedCredManAccessPrivilegeIFNone="False"
        seTcbPrivilegeIFNone=userright_check_res['seTcbPrivilegeIFNone']
        if seTcbPrivilegeIFNone == "True":
            ck_seTcbPrivilegeIFNone="True"
        else:
            ck_seTcbPrivilegeIFNone="False"
        seMachineAccountPrivilegeIFOnlySpecifiedUserOrArray=userright_check_res['seMachineAccountPrivilegeIFOnlySpecifiedUserOrArray']
        if seMachineAccountPrivilegeIFOnlySpecifiedUserOrArray == "True":
            ck_seMachineAccountPrivilegeIFOnlySpecifiedUserOrArray="True"
        else:
            ck_seMachineAccountPrivilegeIFOnlySpecifiedUserOrArray="False"
        seCreateGlobalPrivilegeIFNone=userright_check_res['seCreateGlobalPrivilegeIFNone']
        if seCreateGlobalPrivilegeIFNone == "True":
            ck_seCreateGlobalPrivilegeIFNone="True"
        else:
            ck_seCreateGlobalPrivilegeIFNone="False"
        seDenyBatchLogonRightIFContainGuests=userright_check_res['seDenyBatchLogonRightIFContainGuests']
        if seDenyBatchLogonRightIFContainGuests == "True":
            ck_seDenyBatchLogonRightIFContainGuests="True"
        else:
            ck_seDenyBatchLogonRightIFContainGuests="False"
        seDenyServiceLogonRightIFContainGuests=userright_check_res['seDenyServiceLogonRightIFContainGuests']
        if seDenyServiceLogonRightIFContainGuests == "True":
            ck_seDenyServiceLogonRightIFContainGuests="True"
        else:
            ck_seDenyServiceLogonRightIFContainGuests="False"
        seDenyInteractiveLogonRightIFContainGuests=userright_check_res['seDenyInteractiveLogonRightIFContainGuests']
        if seDenyInteractiveLogonRightIFContainGuests == "True":
            ck_seDenyInteractiveLogonRightIFContainGuests="True"
        else:
            ck_seDenyInteractiveLogonRightIFContainGuests="False"
        seRemoteShutdownPrivilegeIFOnlySpecifiedUserOrArray=userright_check_res['seRemoteShutdownPrivilegeIFOnlySpecifiedUserOrArray']
        if seRemoteShutdownPrivilegeIFOnlySpecifiedUserOrArray == "True":
            ck_seRemoteShutdownPrivilegeIFOnlySpecifiedUserOrArray="True"
        else:
            ck_seRemoteShutdownPrivilegeIFOnlySpecifiedUserOrArray="False"
        seRelabelPrivilegeIFNone=userright_check_res['seRelabelPrivilegeIFNone']
        if seRelabelPrivilegeIFNone == "True":
            ck_seRelabelPrivilegeIFNone="True"
        else:
            ck_seRelabelPrivilegeIFNone="False"
        seSyncAgentPrivilegeIFNone=userright_check_res['seSyncAgentPrivilegeIFNone']
        if seSyncAgentPrivilegeIFNone == "True":
            ck_seSyncAgentPrivilegeIFNone="True"
        else:
            ck_seSyncAgentPrivilegeIFNone="False"
        secureoption_check_res=windowsScanResDict['secureoption_check_res']
        enableGuestAccount=secureoption_check_res['enableGuestAccount']
        if enableGuestAccount == "True":
            ck_enableGuestAccount="True"
        else:
            ck_enableGuestAccount="False"
        limitBlankPasswordUse=secureoption_check_res['limitBlankPasswordUse']
        if limitBlankPasswordUse == "True":
            ck_limitBlankPasswordUse="True"
        else:
            ck_limitBlankPasswordUse="False"
        newAdministratorName=secureoption_check_res['newAdministratorName']
        if newAdministratorName == "True":
            ck_newAdministratorName="True"
        else:
            ck_newAdministratorName="False"
        newGuestName=secureoption_check_res['newGuestName']
        if newGuestName == "True":
            ck_newGuestName="True"
        else:
            ck_newGuestName="False"
        dontDisplayLastUserName=secureoption_check_res['dontDisplayLastUserName']
        if dontDisplayLastUserName == "True":
            ck_dontDisplayLastUserName="True"
        else:
            ck_dontDisplayLastUserName="False"
        disableCAD=secureoption_check_res['disableCAD']
        if disableCAD == "True":
            ck_disableCAD="True"
        else:
            ck_disableCAD="False"
        inactivityTimeoutSecs=secureoption_check_res['inactivityTimeoutSecs']
        if inactivityTimeoutSecs != "False" and int(inactivityTimeoutSecs) <= 900:
            ck_inactivityTimeoutSecs="True"
        else:
            ck_inactivityTimeoutSecs="False"
        enablePlainTextPassword=secureoption_check_res['enablePlainTextPassword']
        if enablePlainTextPassword == "True":
            ck_enablePlainTextPassword="True"
        else:
            ck_enablePlainTextPassword="False"
        autoDisconnect=secureoption_check_res['autoDisconnect']
        if autoDisconnect != "False" and int(autoDisconnect) >= 15:
            ck_autoDisconnect="True"
        else:
            ck_autoDisconnect="False"
        noLMHash=secureoption_check_res['noLMHash']
        if noLMHash == "True":
            ck_noLMHash="True"
        else:
            ck_noLMHash="False"
        lsaAnonymousNameLookup=secureoption_check_res['lsaAnonymousNameLookup']
        if lsaAnonymousNameLookup == "True":
            ck_lsaAnonymousNameLookup="True"
        else:
            ck_lsaAnonymousNameLookup="False"
        restrictAnonymousSAM=secureoption_check_res['restrictAnonymousSAM']
        if restrictAnonymousSAM == "True":
            ck_restrictAnonymousSAM="True"
        else:
            ck_restrictAnonymousSAM="False"
        restrictAnonymous=secureoption_check_res['restrictAnonymous']
        if restrictAnonymous == "True":
            ck_restrictAnonymous="True"
        else:
            ck_restrictAnonymous="False"
        clearPageFileAtShutdown=secureoption_check_res['clearPageFileAtShutdown']
        if clearPageFileAtShutdown == "True":
            ck_clearPageFileAtShutdown="True"
        else:
            ck_clearPageFileAtShutdown="False"
        portsecure_check_res=windowsScanResDict['portsecure_check_res']
        rdpPort=portsecure_check_res['rdpPort']
        if int(rdpPort) != 3389:
            ck_rdpPort="True"
        else:
            ck_rdpPort="False"
        systemsecure_check_res=windowsScanResDict['systemsecure_check_res']
        autoRunRes=systemsecure_check_res['autoRunRes']
        if autoRunRes != "False" and int(autoRunRes) >= 233:
            ck_autoRunRes="True"
        else:
            ck_autoRunRes="False"
        try:
            with transaction.atomic():
                models.WindowsScanResMeta.objects.get_or_create(scanTime=scanTime,macaddr=macaddr,windowsScanResMetaData=bodyData)
                models.WindowsScanRes.objects.get_or_create(scanTime=scanTime,osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList,passwordHistorySize=passwordHistorySize,maximumPasswordAge=maximumPasswordAge,minimumPasswordAge=minimumPasswordAge,passwordComplexity=passwordComplexity,clearTextPassword=clearTextPassword,minimumPasswordLength=minimumPasswordLength,lockoutDuration=lockoutDuration,lockoutBadCount=lockoutBadCount,resetLockoutCount=resetLockoutCount,auditPolicyChange=auditPolicyChange,auditLogonEvents=auditLogonEvents,auditObjectAccess=auditObjectAccess,auditProcessTracking=auditProcessTracking,auditDSAccess=auditDSAccess,auditSystemEvents=auditSystemEvents,auditAccountLogon=auditAccountLogon,auditAccountManage=auditAccountManage,seTrustedCredManAccessPrivilegeIFNone=seTrustedCredManAccessPrivilegeIFNone,seTcbPrivilegeIFNone=seTcbPrivilegeIFNone,seMachineAccountPrivilegeIFOnlySpecifiedUserOrArray=seMachineAccountPrivilegeIFOnlySpecifiedUserOrArray,seCreateGlobalPrivilegeIFNone=seCreateGlobalPrivilegeIFNone,seDenyBatchLogonRightIFContainGuests=seDenyBatchLogonRightIFContainGuests,seDenyServiceLogonRightIFContainGuests=seDenyServiceLogonRightIFContainGuests,seDenyInteractiveLogonRightIFContainGuests=seDenyInteractiveLogonRightIFContainGuests,seRemoteShutdownPrivilegeIFOnlySpecifiedUserOrArray=seRemoteShutdownPrivilegeIFOnlySpecifiedUserOrArray,seRelabelPrivilegeIFNone=seRelabelPrivilegeIFNone,seSyncAgentPrivilegeIFNone=seSyncAgentPrivilegeIFNone,enableGuestAccount=enableGuestAccount,limitBlankPasswordUse=limitBlankPasswordUse,newAdministratorName=newAdministratorName,newGuestName=newGuestName,dontDisplayLastUserName=dontDisplayLastUserName,disableCAD=disableCAD,inactivityTimeoutSecs=inactivityTimeoutSecs,enablePlainTextPassword=enablePlainTextPassword,autoDisconnect=autoDisconnect,noLMHash=noLMHash,lsaAnonymousNameLookup=lsaAnonymousNameLookup,restrictAnonymousSAM=restrictAnonymousSAM,restrictAnonymous=restrictAnonymous,clearPageFileAtShutdown=clearPageFileAtShutdown,rdpPort=rdpPort,autoRunRes=autoRunRes)
                models.WindowsCheckRes.objects.get_or_create(scanTime=scanTime,osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList,passwordHistorySize=ck_passwordHistorySize,maximumPasswordAge=ck_maximumPasswordAge,minimumPasswordAge=ck_minimumPasswordAge,passwordComplexity=ck_passwordComplexity,clearTextPassword=ck_clearTextPassword,minimumPasswordLength=ck_minimumPasswordLength,lockoutDuration=ck_lockoutDuration,lockoutBadCount=ck_lockoutBadCount,resetLockoutCount=ck_resetLockoutCount,auditPolicyChange=ck_auditPolicyChange,auditLogonEvents=ck_auditLogonEvents,auditObjectAccess=ck_auditObjectAccess,auditProcessTracking=ck_auditProcessTracking,auditDSAccess=ck_auditDSAccess,auditSystemEvents=ck_auditSystemEvents,auditAccountLogon=ck_auditAccountLogon,auditAccountManage=ck_auditAccountManage,seTrustedCredManAccessPrivilegeIFNone=ck_seTrustedCredManAccessPrivilegeIFNone,seTcbPrivilegeIFNone=ck_seTcbPrivilegeIFNone,seMachineAccountPrivilegeIFOnlySpecifiedUserOrArray=ck_seMachineAccountPrivilegeIFOnlySpecifiedUserOrArray,seCreateGlobalPrivilegeIFNone=ck_seCreateGlobalPrivilegeIFNone,seDenyBatchLogonRightIFContainGuests=ck_seDenyBatchLogonRightIFContainGuests,seDenyServiceLogonRightIFContainGuests=ck_seDenyServiceLogonRightIFContainGuests,seDenyInteractiveLogonRightIFContainGuests=ck_seDenyInteractiveLogonRightIFContainGuests,seRemoteShutdownPrivilegeIFOnlySpecifiedUserOrArray=ck_seRemoteShutdownPrivilegeIFOnlySpecifiedUserOrArray,seRelabelPrivilegeIFNone=ck_seRelabelPrivilegeIFNone,seSyncAgentPrivilegeIFNone=ck_seSyncAgentPrivilegeIFNone,enableGuestAccount=ck_enableGuestAccount,limitBlankPasswordUse=ck_limitBlankPasswordUse,newAdministratorName=ck_newAdministratorName,newGuestName=ck_newGuestName,dontDisplayLastUserName=ck_dontDisplayLastUserName,disableCAD=ck_disableCAD,inactivityTimeoutSecs=ck_inactivityTimeoutSecs,enablePlainTextPassword=ck_enablePlainTextPassword,autoDisconnect=ck_autoDisconnect,noLMHash=ck_noLMHash,lsaAnonymousNameLookup=ck_lsaAnonymousNameLookup,restrictAnonymousSAM=ck_restrictAnonymousSAM,restrictAnonymous=ck_restrictAnonymous,clearPageFileAtShutdown=ck_clearPageFileAtShutdown,rdpPort=ck_rdpPort,autoRunRes=ck_autoRunRes)
                models.AllScanResRecord.objects.get_or_create(scanTime=scanTime,scanType="OS",osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList)
                vulnCheckResList=windows_vuln_check_res_store(data=windowsVulnScanResDict)
                models.VulnCheckRes.objects.get_or_create(scanTime=scanTime,scanType="Windows",osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList,vulnCheckRes=json.dumps(vulnCheckResList))
                return HttpResponse("success")
                raise DatabaseError
        except DatabaseError:
            return HttpResponse("0oops,something is wrong")
    else:
        return HttpResponse("0oops,something is wrong")
def middleware_check_res_store(data={}):
    basic_info=data['basic_info']
    middlewareCheckResult=data['middleware_check_result']
    redis_check_res=middlewareCheckResult['redis_check_res']
    nginx_check_res=middlewareCheckResult['nginx_check_res']
    tomcat_check_res=middlewareCheckResult['tomcat_check_res']
    scanTime=basic_info['scanTime']
    hostname=basic_info['hostname']
    macaddr=basic_info['macaddr']
    ipList=basic_info['macaddr']
    osVersion=basic_info['osVersion']
def linux_vuln_check_res_store(data={}):
    basic_info=data['basic_info']
    linux_vuln_scan_res=data['vuln_scan_res']
    os=linux_vuln_scan_res['os']
    arc=linux_vuln_scan_res['arc']
    linux_vuln_scan_list=linux_vuln_scan_res['vulnScanList']
    # linux_vuln_scan_list=[["kbd", "1.15.5", "Centos"], ["setup", "2.8.71", "Centos"], ["libstdc++", "4.8.5", "Centos"]]
    # os="Linux"
    # arc="x86_64"
    return baseline.linuxVulnScanUtil.vulnCheck(data=linux_vuln_scan_list,os=os,arc=arc)

@csrf_exempt
def linux_scan_res_report(request):

    if request.method == "POST":
        bodyData=request.body
        # 从post的body体中读取并反序列化为dict数据
        scanResDict=json.loads(bodyData)
        linuxScanResDict=scanResDict['os_scan_result']
        middlewareCheckResDict=scanResDict['middleware_check_result']
        # print(middlewareCheckResDict)
        linuxVulnScanResDict=scanResDict['vuln_scan_result']
        # print(linuxVulnScanResDict)
        #scanTime = time.strftime('%Y-%m-%d %H:%M:%S')
        # 从dict数据中解析并读取数据
        basic_info=linuxScanResDict['basic_info']
        scanTime=basic_info['scanTime']
        hostname=basic_info['hostname']
        macaddr=basic_info['macaddr']
        ipList=basic_info['ipList']
        kernelVersion=basic_info['kernelVersion']
        osVersion=basic_info['osVersion']
        init_check_res=linuxScanResDict['init_check_res']
        tmp_partition_info=init_check_res['tmp_partition_info']
        tmpIfSeparate=tmp_partition_info['tmpIfSeparate']
        if tmpIfSeparate == "True":
            ck_tmpIfSeparate="True"
        else:
            ck_tmpIfSeparate="False"
        tmpIfNoexec=tmp_partition_info['tmpIfNoexec']
        if tmpIfNoexec == "True":
            ck_tmpIfNoexec="True"
        else:
            ck_tmpIfNoexec="False"
        tmpIfNosuid=tmp_partition_info['tmpIfNosuid']
        ck_tmpIfNosuid="True" if tmpIfNosuid == "True" else "False"
        boot_secure_info=init_check_res['boot_secure_info']
        grubcfgIfExist=boot_secure_info['grubcfgIfExist']
        grubcfgPermission=boot_secure_info['grubcfgPermission']
        ck_grubcfgPermissionLE600="True" if grubcfgIfExist == "True" and int(grubcfgPermission) <= 600 else "False"
        grubcfgIfSetPasswd=boot_secure_info['grubcfgIfSetPasswd']
        ck_grubcfgIfSetPasswd="True" if grubcfgIfExist == "True" and grubcfgIfSetPasswd == "True" else "False"
        singleUserModeIfNeedAuth=boot_secure_info['singleUserModeIfNeedAuth']
        ck_singleUserModeIfNeedAuth="True" if singleUserModeIfNeedAuth == "True" else "False"
        selinuxStateIfEnforcing=boot_secure_info['selinuxStateIfEnforcing']
        ck_selinuxStateIfEnforcing="True" if selinuxStateIfEnforcing == "True" else "False"
        selinuxPolicyIfConfigured=boot_secure_info['selinuxPolicyIfConfigured']
        ck_selinuxPolicyIfConfigured="True" if selinuxPolicyIfConfigured == "True" else "False"
        service_check_res=linuxScanResDict['service_check_res']
        timeSyncServerIfConfigured=service_check_res['timeSyncServerIfConfigured']
        ck_timeSyncServerIfConfigured="True" if timeSyncServerIfConfigured == "True" else "False"
        x11windowIfNotInstalled=service_check_res['x11windowIfNotInstalled']
        ck_x11windowIfNotInstalled="True" if x11windowIfNotInstalled == "True" else "False"
        network_check_res=linuxScanResDict['network_check_res']
        hostsAllowFileIfExist=network_check_res['hostsAllowFileIfExist']
        hostsAllowFilePermission=network_check_res['hostsAllowFilePermission']
        ck_hostsAllowFilePermission="True" if hostsAllowFileIfExist == "True" and int(hostsAllowFilePermission) <= 644 else "False"
        hostsAllowFileIfConfigured=network_check_res['hostsAllowFileIfConfigured']
        ck_hostsAllowFileIfConfigured="True" if hostsAllowFileIfExist == "True" and hostsAllowFileIfConfigured == "True" else "False"
        hostsDenyFileIfExist=network_check_res['hostsDenyFileIfExist']
        hostsDenyFilePermission=network_check_res['hostsDenyFilePermission']
        ck_hostsDenyFilePermission="True" if hostsDenyFileIfExist == "True" and int(hostsDenyFilePermission) <= 644 else "False"
        hostsDenyFileIfConfigured=network_check_res['hostsDenyFileIfConfigured']
        ck_hostsDenyFileIfConfigured="True" if hostsDenyFileIfExist == "True" and hostsDenyFileIfConfigured == "True" else "False"
        iptablesIfInstalled=network_check_res['iptablesIfInstalled']
        ck_iptablesIfInstalled="True" if iptablesIfInstalled == "True" else "False"
        iptablesInputPolicyIfDrop=network_check_res['iptablesInputPolicyIfDrop']
        ck_iptablesInputPolicyIfDrop="True" if iptablesIfInstalled == "True" and iptablesInputPolicyIfDrop == "True" else "False"
        iptablesOutputPolicyIfDrop=network_check_res['iptablesOutputPolicyIfDrop']
        ck_iptablesOutputPolicyIfDrop="True" if iptablesIfInstalled == "True" and iptablesOutputPolicyIfDrop == "True" else "False"
        auditd_check_res=linuxScanResDict['auditd_check_res']
        auditd_config_info=auditd_check_res['auditd_config_info']
        auditdIfEnabled=auditd_config_info['auditdIfEnabled']
        ck_auditdIfEnabled="True" if auditdIfEnabled == "True" else "False"
        auditdconfIfExist=auditd_config_info['auditdconfIfExist']
        auditdIfSetMaxLogFile=auditd_config_info['auditdIfSetMaxLogFile']
        ck_auditdIfSetMaxLogFile="True" if auditdconfIfExist == "True" and auditdIfSetMaxLogFile != "False" and int(auditdIfSetMaxLogFile) >= 8 else "False"
        auditdIfSetMaxLogFileAction=auditd_config_info['auditdIfSetMaxLogFileAction']
        ck_auditdIfSetMaxLogFileAction="True" if auditdconfIfExist == "True" and ("keep_logs" in auditdIfSetMaxLogFileAction.lower() or "rotate" in auditdIfSetMaxLogFileAction.lower()) else "False"
        auditdIfSetSpaceLeftAction=auditd_config_info['auditdIfSetSpaceLeftAction']
        ck_auditdIfSetSpaceLeftAction="True" if auditdconfIfExist == "True" and "ignore" not in auditdIfSetSpaceLeftAction.lower() and "rotate" not in auditdIfSetSpaceLeftAction.lower() else "False"
        auditdIfSetNumLogs=auditd_config_info['auditdIfSetNumLogs']
        ck_auditdIfSetNumLogs="True" if auditdconfIfExist == "True" and int(auditdIfSetNumLogs) >= 5 else "False"
        auditd_rules_info=auditd_check_res['auditd_rules_info']
        auditdRulesIfExist=auditd_rules_info['auditdRulesIfExist']
        auditdRulesIfNotNull=auditd_rules_info['auditdRulesIfNotNull']
        auditdIfCheckTimechange=auditd_rules_info['auditdIfCheckTimechange']
        ck_auditdIfCheckTimechange="True" if auditdRulesIfNotNull == "True" and auditdIfCheckTimechange == "True" else "False"
        auditdRulesCheckedUserandgroupfile=auditd_rules_info['auditdRulesCheckedUserandgroupfile']
        auditdRulesNotCheckedUserandgroupfile=auditd_rules_info['auditdRulesNotCheckedUserandgroupfile']
        ck_auditdRulesNotCheckedUserandgroupfile="True" if auditdRulesIfNotNull == "True"  and len(auditdRulesNotCheckedUserandgroupfile) == 0 else "False"
        auditdRulesCheckedNetworkenv=auditd_rules_info['auditdRulesCheckedNetworkenv']
        auditdRulesNotCheckedNetworkenv=auditd_rules_info['auditdRulesNotCheckedNetworkenv']
        ck_auditdRulesNotCheckedNetworkenv="True" if auditdRulesIfNotNull == "True" and len(auditdRulesNotCheckedNetworkenv) == 0 else "False"
        auditdRulesCheckedMACchange=auditd_rules_info['auditdRulesCheckedMACchange']
        auditdRulesNotCheckedMACchange=auditd_rules_info['auditdRulesNotCheckedMACchange']
        ck_auditdRulesNotCheckedMACchange="True" if auditdRulesIfNotNull == "True" and len(auditdRulesNotCheckedMACchange) == 0 else "False"
        auditdRulesCheckedLoginoutEvents=auditd_rules_info['auditdRulesCheckedLoginoutEvents']
        auditdRulesNotCheckedLoginoutEvents=auditd_rules_info['auditdRulesNotCheckedLoginoutEvents']
        ck_auditdRulesNotCheckedLoginoutEvents="True" if auditdRulesIfNotNull == "True" and len(auditdRulesNotCheckedMACchange) == 0 else "False"
        auditdRulesCheckedDACChangeSyscall=auditd_rules_info['auditdRulesCheckedDACChangeSyscall']
        auditdRulesNotCheckedDACChangeSyscall=auditd_rules_info['auditdRulesNotCheckedDACChangeSyscall']
        ck_auditdRulesNotCheckedDACChangeSyscall="True" if auditdRulesIfNotNull == "True" and len(auditdRulesNotCheckedDACChangeSyscall) == 0 else "False"
        auditdRulesCheckedFileAccessAttemptSyscall=auditd_rules_info['auditdRulesCheckedFileAccessAttemptSyscall']
        auditdRulesNotCheckedFileAccessAttemptSyscall=auditd_rules_info['auditdRulesNotCheckedFileAccessAttemptSyscall']
        ck_auditdRulesNotCheckedFileAccessAttemptSyscall="True" if auditdRulesIfNotNull == "True" and len(auditdRulesNotCheckedFileAccessAttemptSyscall) == 0 else "False"
        auditdRulesCheckedPrivilegedCommand=auditd_rules_info['auditdRulesCheckedPrivilegedCommand']
        auditdRulesNotCheckedPrivilegedCommand=auditd_rules_info['auditdRulesNotCheckedPrivilegedCommand']
        ck_auditdRulesNotCheckedPrivilegedCommand="True" if auditdRulesIfNotNull == "True" and len(auditdRulesCheckedPrivilegedCommand) == 0 else "False"
        auditdRulesCheckedSudoerFile=auditd_rules_info['auditdRulesCheckedSudoerFile']
        auditdRulesNotCheckedSudoerFile=auditd_rules_info['auditdRulesNotCheckedSudoerFile']
        ck_auditdRulesNotCheckedSudoerFile="True" if auditdRulesIfNotNull == "True" and len(auditdRulesNotCheckedSudoerFile) == 0 else "False"
        auditdRulesIfImmutable=auditd_rules_info['auditdRulesIfImmutable']
        ck_auditdRulesIfImmutable="True" if auditdRulesIfNotNull == "True" and auditdRulesIfImmutable == "True" else "False"
        log_check_res=linuxScanResDict['log_check_res']
        rsyslogIfEnabled=log_check_res['rsyslogIfEnabled']
        ck_rsyslogIfEnabled="True" if rsyslogIfEnabled == "True" else "False"
        authentication_check_res=linuxScanResDict['authentication_check_res']
        crond_config_info=authentication_check_res['crond_config_info']
        crondIfEnabled=crond_config_info['crondIfEnabled']
        ck_crondIfEnabled="True" if crondIfEnabled == "True" else "False"
        crondConfigFilenameArray=crond_config_info['crondConfigFilenameArray']
        crondConfigFilePermissionArray=crond_config_info['crondConfigFilePermissionArray']
        ck_crondConfigFilePermissionArray="True"
        for fPerm in crondConfigFilePermissionArray.split(";"):
            if len(fPerm) != 0:
                if "False" in fPerm or int(fPerm) > 700:
                    ck_crondConfigFilePermissionArray="False"
                    break
        crondallowdenyFilenameArray=crond_config_info['crondallowdenyFilenameArray']
        crondallowdenyFileIfExistArray=crond_config_info['crondallowdenyFileIfExistArray']
        crondallowdenyFilePermissionArray=crond_config_info['crondallowdenyFilePermissionArray']
        ck_crondallowdenyFilePermissionArray="True"
        for fPerm in crondallowdenyFilePermissionArray.split(";"):
            if len(fPerm) != 0:
                if "False" in fPerm or int(fPerm) > 700:
                    ck_crondallowdenyFilePermissionArray="False"
        crondallowdenyFileOwnerArray=crond_config_info['crondallowdenyFileOwnerArray']
        sshd_config_info=authentication_check_res['sshd_config_info']
        sshdIfEnabled=sshd_config_info['sshdIfEnabled']
        sshdConfigFilePermission=sshd_config_info['sshdConfigFilePermission']
        ck_sshdConfigFilePermission="True" if sshdIfEnabled != "True" or sshdConfigFilePermission != "False" and int(sshdConfigFilePermission) <= 600 else "False"
        sshdIfDisableX11forwarding=sshd_config_info['sshdIfDisableX11forwarding']
        ck_sshdIfDisableX11forwarding="True" if sshdIfEnabled != "True" or sshdIfDisableX11forwarding == "True" else "False"
        sshdIfSetMaxAuthTries=sshd_config_info['sshdIfSetMaxAuthTries']
        ck_sshdIfSetMaxAuthTries="True" if sshdIfEnabled != "True" or sshdIfSetMaxAuthTries != "False" and int(sshdIfSetMaxAuthTries) >= 4 else "False"
        sshdIfEnableIgnoreRhosts=sshd_config_info['sshdIfEnableIgnoreRhosts']
        ck_sshdIfEnableIgnoreRhosts="True" if sshdIfEnabled != "True" or sshdIfEnableIgnoreRhosts == "True" else "False"
        sshdIfDisableHostbasedAuthentication=sshd_config_info['sshdIfDisableHostbasedAuthentication']
        ck_sshdIfDisableHostbasedAuthentication="True" if sshdIfEnabled != "True" or sshdIfDisableHostbasedAuthentication == "True" else "False"
        sshdIfDisablePermitRootLogin=sshd_config_info['sshdIfDisablePermitRootLogin']
        ck_sshdIfDisablePermitRootLogin="True" if sshdIfEnabled != "True" or sshdIfDisablePermitRootLogin == "True" else "False"
        sshdIfDisablePermitEmptyPasswords=sshd_config_info['sshdIfDisablePermitEmptyPasswords']
        ck_sshdIfDisablePermitEmptyPasswords="True" if sshdIfEnabled != "True" or sshdIfDisablePermitEmptyPasswords == "True" else "False"
        sshdIfDisablePermitUserEnvironment=sshd_config_info['sshdIfDisablePermitUserEnvironment']
        ck_sshdIfDisablePermitUserEnvironment="True" if sshdIfEnabled != "True" or sshdIfDisablePermitUserEnvironment == "True" else "False"
        sshdIfSpecificMACs=sshd_config_info['sshdIfSpecificMACs']
        ck_sshdIfSpecificMACs="True" if sshdIfEnabled != "True" or sshdIfSpecificMACs == "True" else "False"
        sshdIfSetClientAliveInterval=sshd_config_info['sshdIfSetClientAliveInterval']
        ck_sshdIfSetClientAliveInterval="True" if sshdIfEnabled != "True" or sshdIfSetClientAliveInterval != "False" and int(sshdIfSetClientAliveInterval) <= 180 else "False"
        sshdIfSetLoginGraceTime=sshd_config_info['sshdIfSetLoginGraceTime']
        ck_sshdIfSetLoginGraceTime="True" if sshdIfEnabled != "True" or sshdIfSetLoginGraceTime != "False" and int(sshdIfSetLoginGraceTime) <= 120 else "False"
        pam_config_info=authentication_check_res['pam_config_info']
        pamPwqualityconfIfExist=pam_config_info['pamPwqualityconfIfExist']
        pamIfSetMinlen=pam_config_info['pamIfSetMinlen']
        ck_pamIfSetMinlen="True" if pamIfSetMinlen != "False" and int(pamIfSetMinlen) >= 8 else "False"
        pamIfSetMinclass=pam_config_info['pamIfSetMinclass']
        ck_pamIfSetMinclass="True" if pamIfSetMinclass != "False" and int(pamIfSetMinclass) >= 3 else "False"
        sshdSetedLockAndUnlockTimeFiles=pam_config_info['sshdSetedLockAndUnlockTimeFiles']
        sshdNotSetedLockAndUnlockTimeFiles=pam_config_info['sshdNotSetedLockAndUnlockTimeFiles']
        ck_sshdNotSetedLockAndUnlockTimeFiles="True" if len(sshdNotSetedLockAndUnlockTimeFiles) == 0 else "False"
        sshdPamdFileArray=pam_config_info['sshdPamdFileArray']
        sshdPamdFileReuseLimitArray=pam_config_info['sshdPamdFileReuseLimitArray']
        ck_sshdPamdFileReuseLimitArray="True" if "False" not in sshdPamdFileReuseLimitArray and "False" not in [int(i) > 5 for i in sshdPamdFileReuseLimitArray.split(";")[:-1]] else "False"
        sshdPamdFileIfSetSha512Array=pam_config_info['sshdPamdFileIfSetSha512Array']
        ck_sshdPamdFileIfSetSha512Array="True" if "False" not in sshdPamdFileIfSetSha512Array else "False"
        account_config_info=authentication_check_res['account_config_info']
        accountPassMaxDays=account_config_info['accountPassMaxDays']
        ck_accountPassMaxDays="True" if len(accountPassMaxDays) != 0 and int(accountPassMaxDays)  <= 90 else "False"
        accountPassMinDays=account_config_info['accountPassMinDays']
        ck_accountPassMinDays="True" if len(accountPassMinDays) != 0 and int(accountPassMinDays)  >= 1 else "False"
        accountPassWarnDays=account_config_info['accountPassWarnDays']
        ck_accountPassWarnDays="True" if len(accountPassWarnDays) != 0 and int(accountPassWarnDays)  >= 7 else "False"
        accountPassAutolockInactiveDays=account_config_info['accountPassAutolockInactiveDays']
        ck_accountPassAutolockInactiveDays="True" if len(accountPassAutolockInactiveDays) != 0 and int(accountPassAutolockInactiveDays) != -1 and int(accountPassAutolockInactiveDays) <= 365 else "False"
        accountShouldUnloginArray=account_config_info['accountShouldUnloginArray']
        ck_accountShouldUnloginArray="True" if len(accountShouldUnloginArray) == 0 else "False"
        accountGIDOfRoot=account_config_info['accountGIDOfRoot']
        ck_accountGIDOfRoot="True" if int(accountGIDOfRoot) == 0 else "False"
        accountProfileFileArray=account_config_info['accountProfileFileArray']
        accountProfileTMOUTArray=account_config_info['accountProfileTMOUTArray']
        ck_accountProfileTMOUTArray="True" if "False" not in accountProfileTMOUTArray and "False" not in [int(i) <= 900 for i in accountProfileTMOUTArray.split(";")[:-1]] else "False"
        accountIfSetUsersCanAccessSuCommand=account_config_info['accountIfSetUsersCanAccessSuCommand']
        ck_accountIfSetUsersCanAccessSuCommand="True" if "False" not in accountIfSetUsersCanAccessSuCommand else "False"
        system_check_res=linuxScanResDict['system_check_res']
        file_permission_info=system_check_res['file_permission_info']
        importantFilenameArray=file_permission_info['importantFilenameArray']
        importantFilePermissionArray=file_permission_info['importantFilePermissionArray']
        tmpCount=0
        for i in importantFilePermissionArray.split(";")[:-1]:
            if i == "0000":
                tmpCount = tmpCount + 1
            if int(i) <= 644 :
                tmpCount = tmpCount + 1
        ck_importantFilePermissionArray="True" if tmpCount == 12 else "False"
        importantFileUidgidArray=file_permission_info['importantFileUidgidArray']
        ck_importantFileUidgidArray="True" if "False" not in ["0 0" == i for i in importantFileUidgidArray.split(";")[:-1]] else "False"
        usergroup_config_info=system_check_res['usergroup_config_info']
        userIfSetPasswdOrArray=usergroup_config_info['userIfSetPasswdOrArray']
        ck_userIfSetPasswdOrArray="True" if userIfSetPasswdOrArray == "True" else "False"
        uid0OnlyRootOrArray=usergroup_config_info['uid0OnlyRootOrArray']
        ck_uid0OnlyRootOrArray="True" if uid0OnlyRootOrArray == "True" else "False"
        pathDirIfNotHasDot=usergroup_config_info['pathDirIfNotHasDot']
        ck_pathDirIfNotHasDot="True" if pathDirIfNotHasDot == "True" else "False"
        pathDirPermissionHasGWArray=usergroup_config_info['pathDirPermissionHasGWArray']
        ck_pathDirPermissionHasGWArray="True" if len(pathDirPermissionHasGWArray) == 0 else "False"
        pathDirPermissionHasOWArray=usergroup_config_info['pathDirPermissionHasOWArray']
        ck_pathDirPermissionHasOWArray="True" if len(pathDirPermissionHasOWArray) == 0 else "False"
        pathDirOwnerIsNotRootArray=usergroup_config_info['pathDirOwnerIsNotRootArray']
        pathDirDoesNotExistOrNotDirArray=usergroup_config_info['pathDirDoesNotExistOrNotDirArray']
        ck_pathDirDoesNotExistOrNotDirArray="True" if len(pathDirDoesNotExistOrNotDirArray) == 0 else "False"
        userArray=usergroup_config_info['userArray']
        userHomeDirIfExistArray=usergroup_config_info['userHomeDirIfExistArray']
        ck_userHomeDirIfExistArray="True" if "False" not in userHomeDirIfExistArray else "False"
        userHomeDirPermissionArray=usergroup_config_info['userHomeDirPermissionArray']
        ck_userHomeDirPermissionArray="True" if "False" not in userHomeDirPermissionArray and "False" not in [int(i) > 750 for i in userHomeDirPermissionArray.split(";")[:-1]] else "False"
        userIfOwnTheirHomeDirArray=usergroup_config_info['userIfOwnTheirHomeDirArray']
        ck_userIfOwnTheirHomeDirArray="True" if "False" not in userIfOwnTheirHomeDirArray else "False"
        userHomeDirIfHasGWorOWDotFileArray=usergroup_config_info['userHomeDirIfHasGWorOWDotFileArray']
        ck_userHomeDirIfHasGWorOWDotFileArray="True" if "False" not in userHomeDirIfHasGWorOWDotFileArray else "False"
        userHomeDirIfHasOtherFileArray=usergroup_config_info['userHomeDirIfHasOtherFileArray']
        ck_userHomeDirIfHasOtherFileArray="True" if "False" not in userHomeDirIfHasOtherFileArray else "False"
        groupNotExistInetcgroup=usergroup_config_info['groupNotExistInetcgroup']
        ck_groupNotExistInetcgroup="True" if len(groupNotExistInetcgroup) == 0 else "False"
        usersIfHasUniqueUIDArray=usergroup_config_info['usersIfHasUniqueUIDArray']
        ck_usersIfHasUniqueUIDArray="True" if len(usersIfHasUniqueUIDArray) == 0 else "False"
        groupsIfHasUniqueGIDArray=usergroup_config_info['groupsIfHasUniqueGIDArray'] 
        ck_groupsIfHasUniqueGIDArray="True" if len(groupsIfHasUniqueGIDArray) == 0 else "False"
        # 向LinuxScanResMeta表中插入数据
        try:
            with transaction.atomic():
                models.LinuxScanResMeta.objects.get_or_create(scanTime=scanTime,macaddr=macaddr,linuxScanResMetaData=bodyData)
                models.LinuxScanRes.objects.get_or_create(scanTime=scanTime,hostname=hostname,macaddr=macaddr,ipList=ipList,kernelVersion=kernelVersion,osVersion=osVersion,tmpIfSeparate=tmpIfSeparate,tmpIfNoexec=tmpIfNoexec,tmpIfNosuid=tmpIfNosuid,grubcfgIfExist=grubcfgIfExist,grubcfgPermission=grubcfgPermission,grubcfgIfSetPasswd=grubcfgIfSetPasswd,singleUserModeIfNeedAuth=singleUserModeIfNeedAuth,selinuxStateIfEnforcing=selinuxStateIfEnforcing,selinuxPolicyIfConfigured=selinuxPolicyIfConfigured,timeSyncServerIfConfigured=timeSyncServerIfConfigured,x11windowIfNotInstalled=x11windowIfNotInstalled,hostsAllowFileIfExist=hostsAllowFileIfExist,hostsAllowFilePermission=hostsAllowFilePermission,hostsAllowFileIfConfigured=hostsAllowFileIfConfigured,hostsDenyFileIfExist=hostsDenyFileIfExist,hostsDenyFilePermission=hostsDenyFilePermission,hostsDenyFileIfConfigured=hostsDenyFileIfConfigured,iptablesIfInstalled=iptablesIfInstalled,iptablesInputPolicyIfDrop=iptablesInputPolicyIfDrop,iptablesOutputPolicyIfDrop=iptablesOutputPolicyIfDrop,auditdIfEnabled=auditdIfEnabled,auditdconfIfExist=auditdconfIfExist,auditdIfSetMaxLogFile=auditdIfSetMaxLogFile,auditdIfSetMaxLogFileAction=auditdIfSetMaxLogFileAction,auditdIfSetSpaceLeftAction=auditdIfSetSpaceLeftAction,auditdIfSetNumLogs=auditdIfSetNumLogs,auditdRulesIfExist=auditdRulesIfExist,auditdRulesIfNotNull=auditdRulesIfNotNull,auditdIfCheckTimechange=auditdIfCheckTimechange,auditdRulesCheckedUserandgroupfile=auditdRulesCheckedUserandgroupfile,auditdRulesNotCheckedUserandgroupfile=auditdRulesNotCheckedUserandgroupfile,auditdRulesCheckedNetworkenv=auditdRulesCheckedNetworkenv,auditdRulesNotCheckedNetworkenv=auditdRulesNotCheckedNetworkenv,auditdRulesCheckedMACchange=auditdRulesCheckedMACchange,auditdRulesNotCheckedMACchange=auditdRulesNotCheckedMACchange,auditdRulesCheckedLoginoutEvents=auditdRulesCheckedLoginoutEvents,auditdRulesNotCheckedLoginoutEvents=auditdRulesNotCheckedLoginoutEvents,auditdRulesCheckedDACChangeSyscall=auditdRulesCheckedDACChangeSyscall,auditdRulesNotCheckedDACChangeSyscall=auditdRulesNotCheckedDACChangeSyscall,auditdRulesCheckedFileAccessAttemptSyscall=auditdRulesCheckedFileAccessAttemptSyscall,auditdRulesNotCheckedFileAccessAttemptSyscall=auditdRulesNotCheckedFileAccessAttemptSyscall,auditdRulesCheckedPrivilegedCommand=auditdRulesCheckedPrivilegedCommand,auditdRulesNotCheckedPrivilegedCommand=auditdRulesNotCheckedPrivilegedCommand,auditdRulesCheckedSudoerFile=auditdRulesCheckedSudoerFile,auditdRulesNotCheckedSudoerFile=auditdRulesNotCheckedSudoerFile,auditdRulesIfImmutable=auditdRulesIfImmutable,rsyslogIfEnabled=rsyslogIfEnabled,crondIfEnabled=crondIfEnabled,crondConfigFilenameArray=crondConfigFilenameArray,crondConfigFilePermissionArray=crondConfigFilePermissionArray,crondallowdenyFilenameArray=crondallowdenyFilenameArray,crondallowdenyFileIfExistArray=crondallowdenyFileIfExistArray,crondallowdenyFilePermissionArray=crondallowdenyFilePermissionArray,crondallowdenyFileOwnerArray=crondallowdenyFileOwnerArray,sshdIfEnabled=sshdIfEnabled,sshdConfigFilePermission=sshdConfigFilePermission,sshdIfDisableX11forwarding=sshdIfDisableX11forwarding,sshdIfSetMaxAuthTries=sshdIfSetMaxAuthTries,sshdIfEnableIgnoreRhosts=sshdIfEnableIgnoreRhosts,sshdIfDisableHostbasedAuthentication=sshdIfDisableHostbasedAuthentication,sshdIfDisablePermitRootLogin=sshdIfDisablePermitRootLogin,sshdIfDisablePermitEmptyPasswords=sshdIfDisablePermitEmptyPasswords,sshdIfDisablePermitUserEnvironment=sshdIfDisablePermitUserEnvironment,sshdIfSpecificMACs=sshdIfSpecificMACs,sshdIfSetClientAliveInterval=sshdIfSetClientAliveInterval,sshdIfSetLoginGraceTime=sshdIfSetLoginGraceTime,pamPwqualityconfIfExist=pamPwqualityconfIfExist,pamIfSetMinlen=pamIfSetMinlen,pamIfSetMinclass=pamIfSetMinclass,sshdSetedLockAndUnlockTimeFiles=sshdSetedLockAndUnlockTimeFiles,sshdNotSetedLockAndUnlockTimeFiles=sshdNotSetedLockAndUnlockTimeFiles,sshdPamdFileArray=sshdPamdFileArray,sshdPamdFileReuseLimitArray=sshdPamdFileReuseLimitArray,sshdPamdFileIfSetSha512Array=sshdPamdFileIfSetSha512Array,accountPassMaxDays=accountPassMaxDays,accountPassMinDays=accountPassMinDays,accountPassWarnDays=accountPassWarnDays,accountPassAutolockInactiveDays=accountPassAutolockInactiveDays,accountShouldUnloginArray=accountShouldUnloginArray,accountGIDOfRoot=accountGIDOfRoot,accountProfileFileArray=accountProfileFileArray,accountProfileTMOUTArray=accountProfileTMOUTArray,accountIfSetUsersCanAccessSuCommand=accountIfSetUsersCanAccessSuCommand,importantFilenameArray=importantFilenameArray,importantFilePermissionArray=importantFilePermissionArray,importantFileUidgidArray=importantFileUidgidArray,userIfSetPasswdOrArray=userIfSetPasswdOrArray,uid0OnlyRootOrArray=uid0OnlyRootOrArray,pathDirIfNotHasDot=pathDirIfNotHasDot,pathDirPermissionHasGWArray=pathDirPermissionHasGWArray,pathDirPermissionHasOWArray=pathDirPermissionHasOWArray,pathDirOwnerIsNotRootArray=pathDirOwnerIsNotRootArray,pathDirDoesNotExistOrNotDirArray=pathDirDoesNotExistOrNotDirArray,userArray=userArray,userHomeDirIfExistArray=userHomeDirIfExistArray,userHomeDirPermissionArray=userHomeDirPermissionArray,userIfOwnTheirHomeDirArray=userIfOwnTheirHomeDirArray,userHomeDirIfHasGWorOWDotFileArray=userHomeDirIfHasGWorOWDotFileArray,userHomeDirIfHasOtherFileArray=userHomeDirIfHasOtherFileArray,groupNotExistInetcgroup=groupNotExistInetcgroup,usersIfHasUniqueUIDArray=usersIfHasUniqueUIDArray,groupsIfHasUniqueGIDArray=groupsIfHasUniqueGIDArray)
                models.LinuxCheckRes.objects.get_or_create(scanTime=scanTime,osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList,ck_tmpIfSeparate=ck_tmpIfSeparate,ck_tmpIfNoexec=ck_tmpIfNoexec,ck_tmpIfNosuid=ck_tmpIfNosuid,ck_grubcfgPermissionLE600=ck_grubcfgPermissionLE600,ck_grubcfgIfSetPasswd=ck_grubcfgIfSetPasswd,ck_singleUserModeIfNeedAuth=ck_singleUserModeIfNeedAuth,ck_selinuxStateIfEnforcing=ck_selinuxStateIfEnforcing,ck_selinuxPolicyIfConfigured=ck_selinuxPolicyIfConfigured,ck_timeSyncServerIfConfigured=ck_timeSyncServerIfConfigured,ck_x11windowIfNotInstalled=ck_x11windowIfNotInstalled,ck_hostsAllowFilePermission=ck_hostsAllowFilePermission,ck_hostsAllowFileIfConfigured=ck_hostsAllowFileIfConfigured,ck_hostsDenyFilePermission=ck_hostsDenyFilePermission,ck_hostsDenyFileIfConfigured=ck_hostsDenyFileIfConfigured,ck_iptablesIfInstalled=ck_iptablesIfInstalled,ck_iptablesInputPolicyIfDrop=ck_iptablesInputPolicyIfDrop,ck_iptablesOutputPolicyIfDrop=ck_iptablesOutputPolicyIfDrop,ck_auditdIfEnabled=ck_auditdIfEnabled,ck_auditdIfSetMaxLogFile=ck_auditdIfSetMaxLogFile,ck_auditdIfSetMaxLogFileAction=ck_auditdIfSetMaxLogFileAction,ck_auditdIfSetSpaceLeftAction=ck_auditdIfSetSpaceLeftAction,ck_auditdIfSetNumLogs=ck_auditdIfSetNumLogs,ck_auditdIfCheckTimechange=ck_auditdIfCheckTimechange,ck_auditdRulesNotCheckedUserandgroupfile=ck_auditdRulesNotCheckedUserandgroupfile,ck_auditdRulesNotCheckedNetworkenv=ck_auditdRulesNotCheckedNetworkenv,ck_auditdRulesNotCheckedMACchange=ck_auditdRulesNotCheckedMACchange,ck_auditdRulesNotCheckedDACChangeSyscall=ck_auditdRulesNotCheckedDACChangeSyscall,ck_auditdRulesNotCheckedFileAccessAttemptSyscall=ck_auditdRulesNotCheckedFileAccessAttemptSyscall,ck_auditdRulesNotCheckedLoginoutEvents=ck_auditdRulesNotCheckedLoginoutEvents,ck_auditdRulesNotCheckedPrivilegedCommand=ck_auditdRulesNotCheckedPrivilegedCommand,ck_auditdRulesNotCheckedSudoerFile=ck_auditdRulesNotCheckedSudoerFile,ck_auditdRulesIfImmutable=ck_auditdRulesIfImmutable,ck_rsyslogIfEnabled=ck_rsyslogIfEnabled,ck_crondIfEnabled=ck_crondIfEnabled,ck_crondConfigFilePermissionArray=ck_crondConfigFilePermissionArray,ck_crondallowdenyFilePermissionArray=ck_crondallowdenyFilePermissionArray,ck_sshdConfigFilePermission=ck_sshdConfigFilePermission,ck_sshdIfDisableX11forwarding=ck_sshdIfDisableX11forwarding,ck_sshdIfSetMaxAuthTries=ck_sshdIfSetMaxAuthTries,ck_sshdIfEnableIgnoreRhosts=ck_sshdIfEnableIgnoreRhosts,ck_sshdIfDisableHostbasedAuthentication=ck_sshdIfDisableHostbasedAuthentication,ck_sshdIfDisablePermitRootLogin=ck_sshdIfDisablePermitRootLogin,ck_sshdIfDisablePermitEmptyPasswords=ck_sshdIfDisablePermitEmptyPasswords,ck_sshdIfDisablePermitUserEnvironment=ck_sshdIfDisablePermitUserEnvironment,ck_sshdIfSpecificMACs=ck_sshdIfSpecificMACs,ck_sshdIfSetClientAliveInterval=ck_sshdIfSetClientAliveInterval,ck_sshdIfSetLoginGraceTime=ck_sshdIfSetLoginGraceTime,ck_pamIfSetMinlen=ck_pamIfSetMinlen,ck_pamIfSetMinclass=ck_pamIfSetMinclass,ck_sshdNotSetedLockAndUnlockTimeFiles=ck_sshdNotSetedLockAndUnlockTimeFiles,ck_sshdPamdFileReuseLimitArray=ck_sshdPamdFileReuseLimitArray,ck_sshdPamdFileIfSetSha512Array=ck_sshdPamdFileIfSetSha512Array,ck_accountPassMaxDays=ck_accountPassMaxDays,ck_accountPassMinDays=ck_accountPassMinDays,ck_accountPassWarnDays=ck_accountPassWarnDays,ck_accountPassAutolockInactiveDays=ck_accountPassAutolockInactiveDays,ck_accountShouldUnloginArray=ck_accountShouldUnloginArray,ck_accountGIDOfRoot=ck_accountGIDOfRoot,ck_accountProfileTMOUTArray=ck_accountProfileTMOUTArray,ck_accountIfSetUsersCanAccessSuCommand=ck_accountIfSetUsersCanAccessSuCommand,ck_importantFilePermissionArray=ck_importantFilePermissionArray,ck_importantFileUidgidArray=ck_importantFileUidgidArray,ck_userIfSetPasswdOrArray=ck_userIfSetPasswdOrArray,ck_uid0OnlyRootOrArray=ck_uid0OnlyRootOrArray,ck_pathDirIfNotHasDot=ck_pathDirIfNotHasDot,ck_pathDirPermissionHasGWArray=ck_pathDirPermissionHasGWArray,ck_pathDirPermissionHasOWArray=ck_pathDirPermissionHasOWArray,ck_pathDirDoesNotExistOrNotDirArray=ck_pathDirDoesNotExistOrNotDirArray,ck_userHomeDirIfExistArray=ck_userHomeDirIfExistArray,ck_userHomeDirPermissionArray=ck_userHomeDirPermissionArray,ck_userIfOwnTheirHomeDirArray=ck_userIfOwnTheirHomeDirArray,ck_userHomeDirIfHasGWorOWDotFileArray=ck_userHomeDirIfHasGWorOWDotFileArray,ck_userHomeDirIfHasOtherFileArray=ck_userHomeDirIfHasOtherFileArray,ck_groupNotExistInetcgroup=ck_groupNotExistInetcgroup,ck_usersIfHasUniqueUIDArray=ck_usersIfHasUniqueUIDArray,ck_groupsIfHasUniqueGIDArray=ck_groupsIfHasUniqueGIDArray)
                models.AllScanResRecord.objects.get_or_create(scanTime=scanTime,scanType="OS",osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList)
                models.MiddlewareCheckResMeta.objects.get_or_create(scanTime=scanTime,scanType="linux",osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList,middlewareCheckResMeta=json.dumps(middlewareCheckResDict))
                vulnCheckResList=linux_vuln_check_res_store(data=linuxVulnScanResDict)
                print(vulnCheckResList)
                models.VulnCheckRes.objects.get_or_create(scanTime=scanTime,scanType="linux",osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList,vulnCheckRes=json.dumps(vulnCheckResList))
                return HttpResponse("Success.")
                raise DatabaseError
        except DatabaseError:
            return HttpResponse("0oops,something is wrong")
        # models.LinuxScanResMeta.objects.get_or_create(scanTime=scanTime,macaddr=macaddr,linuxScanResMetaData=bodyData)
        # with open("test.log","a") as f:
        #     f.write("tmpIfSeparate=" + tmpIfSeparate +"\n")
        #     f.write("tmpIfNoexec=" + tmpIfNoexec +"\n")
        #     f.write("tmpIfNosuid=" + tmpIfNosuid +"\n")
        #     f.write("grubcfgIfExist=" + grubcfgIfExist +"\n")
        #     f.write("grubcfgIfSetPasswd=" + grubcfgIfSetPasswd +"\n")
        #     f.write("singleUserModeIfNeedAuth=" + singleUserModeIfNeedAuth +"\n")
        #     f.write("selinuxStateIfEnforcing=" + selinuxStateIfEnforcing +"\n")
        #     f.write("selinuxPolicyIfConfigured=" + selinuxPolicyIfConfigured +"\n")
        #     f.write("timeSyncServerIfConfigured=" + timeSyncServerIfConfigured +"\n")
        #     f.write("x11windowIfNotInstalled=" + x11windowIfNotInstalled +"\n")
        #     f.write("hostsAllowFileIfExist=" + hostsAllowFileIfExist +"\n")
        #     f.write("hostsAllowFileIfConfigured=" + hostsAllowFileIfConfigured +"\n")
        #     f.write("hostsDenyFileIfExist=" + hostsDenyFileIfExist +"\n")
        #     f.write("hostsDenyFileIfConfigured=" + hostsDenyFileIfConfigured +"\n")
        #     f.write("iptablesIfInstalled=" + iptablesIfInstalled +"\n")
        #     f.write("iptablesInputPolicyIfDrop=" + iptablesInputPolicyIfDrop +"\n")
        #     f.write("iptablesOutputPolicyIfDrop=" + iptablesOutputPolicyIfDrop +"\n")
        #     f.write("auditdIfEnabled=" + auditdIfEnabled +"\n")
        #     f.write("auditdconfIfExist=" + auditdconfIfExist +"\n")
        #     f.write("auditdRulesIfExist=" + auditdRulesIfExist +"\n")
        #     f.write("auditdRulesIfNotNull=" + auditdRulesIfNotNull +"\n")
        #     f.write("auditdIfCheckTimechange=" + auditdIfCheckTimechange +"\n")
        #     f.write("auditdRulesIfImmutable=" + auditdRulesIfImmutable +"\n")
        #     f.write("rsyslogIfEnabled=" + rsyslogIfEnabled +"\n")
        #     f.write("crondIfEnabled=" + crondIfEnabled +"\n")
        #     f.write("sshdIfEnabled=" + sshdIfEnabled +"\n")
        #     f.write("sshdIfDisableX11forwarding=" + sshdIfDisableX11forwarding +"\n")
        #     f.write("sshdIfEnableIgnoreRhosts=" + sshdIfEnableIgnoreRhosts +"\n")
        #     f.write("sshdIfDisableHostbasedAuthentication=" + sshdIfDisableHostbasedAuthentication +"\n")
        #     f.write("sshdIfDisablePermitRootLogin=" + sshdIfDisablePermitRootLogin +"\n")
        #     f.write("sshdIfDisablePermitEmptyPasswords=" + sshdIfDisablePermitEmptyPasswords +"\n")
        #     f.write("sshdIfDisablePermitUserEnvironment=" + sshdIfDisablePermitUserEnvironment +"\n")
        #     f.write("sshdIfSpecificMACs=" + sshdIfSpecificMACs +"\n")
        #     f.write("sshdIfSetClientAliveInterval=" + sshdIfSetClientAliveInterval +"\n")
        #     f.write("sshdIfSetLoginGraceTime=" + sshdIfSetLoginGraceTime +"\n")
        #     f.write("pamPwqualityconfIfExist=" + pamPwqualityconfIfExist +"\n")
        # models.LinuxScanRes.objects.get_or_create(scanTime=scanTime,hostname=hostname,macaddr=macaddr,ipList=ipList,kernelVersion=kernelVersion,osVersion=osVersion,tmpIfSeparate=tmpIfSeparate,tmpIfNoexec=tmpIfNoexec,tmpIfNosuid=tmpIfNosuid,grubcfgIfExist=grubcfgIfExist,grubcfgPermission=grubcfgPermission,grubcfgIfSetPasswd=grubcfgIfSetPasswd,singleUserModeIfNeedAuth=singleUserModeIfNeedAuth,selinuxStateIfEnforcing=selinuxStateIfEnforcing,selinuxPolicyIfConfigured=selinuxPolicyIfConfigured,timeSyncServerIfConfigured=timeSyncServerIfConfigured,x11windowIfNotInstalled=x11windowIfNotInstalled,hostsAllowFileIfExist=hostsAllowFileIfExist,hostsAllowFilePermission=hostsAllowFilePermission,hostsAllowFileIfConfigured=hostsAllowFileIfConfigured,hostsDenyFileIfExist=hostsDenyFileIfExist,hostsDenyFilePermission=hostsDenyFilePermission,hostsDenyFileIfConfigured=hostsDenyFileIfConfigured,iptablesIfInstalled=iptablesIfInstalled,iptablesInputPolicyIfDrop=iptablesInputPolicyIfDrop,iptablesOutputPolicyIfDrop=iptablesOutputPolicyIfDrop,auditdIfEnabled=auditdIfEnabled,auditdconfIfExist=auditdconfIfExist,auditdIfSetMaxLogFile=auditdIfSetMaxLogFile,auditdIfSetMaxLogFileAction=auditdIfSetMaxLogFileAction,auditdIfSetSpaceLeftAction=auditdIfSetSpaceLeftAction,auditdIfSetNumLogs=auditdIfSetNumLogs,auditdRulesIfExist=auditdRulesIfExist,auditdRulesIfNotNull=auditdRulesIfNotNull,auditdIfCheckTimechange=auditdIfCheckTimechange,auditdRulesCheckedUserandgroupfile=auditdRulesCheckedUserandgroupfile,auditdRulesNotCheckedUserandgroupfile=auditdRulesNotCheckedUserandgroupfile,auditdRulesCheckedNetworkenv=auditdRulesCheckedNetworkenv,auditdRulesNotCheckedNetworkenv=auditdRulesNotCheckedNetworkenv,auditdRulesCheckedMACchange=auditdRulesCheckedMACchange,auditdRulesNotCheckedMACchange=auditdRulesNotCheckedMACchange,auditdRulesCheckedLoginoutEvents=auditdRulesCheckedLoginoutEvents,auditdRulesNotCheckedLoginoutEvents=auditdRulesNotCheckedLoginoutEvents,auditdRulesCheckedDACChangeSyscall=auditdRulesCheckedDACChangeSyscall,auditdRulesNotCheckedDACChangeSyscall=auditdRulesNotCheckedDACChangeSyscall,auditdRulesCheckedFileAccessAttemptSyscall=auditdRulesCheckedFileAccessAttemptSyscall,auditdRulesNotCheckedFileAccessAttemptSyscall=auditdRulesNotCheckedFileAccessAttemptSyscall,auditdRulesCheckedPrivilegedCommand=auditdRulesCheckedPrivilegedCommand,auditdRulesNotCheckedPrivilegedCommand=auditdRulesNotCheckedPrivilegedCommand,auditdRulesCheckedSudoerFile=auditdRulesCheckedSudoerFile,auditdRulesNotCheckedSudoerFile=auditdRulesNotCheckedSudoerFile,auditdRulesIfImmutable=auditdRulesIfImmutable,rsyslogIfEnabled=rsyslogIfEnabled,crondIfEnabled=crondIfEnabled,crondConfigFilenameArray=crondConfigFilenameArray,crondConfigFilePermissionArray=crondConfigFilePermissionArray,crondallowdenyFilenameArray=crondallowdenyFilenameArray,crondallowdenyFileIfExistArray=crondallowdenyFileIfExistArray,crondallowdenyFilePermissionArray=crondallowdenyFilePermissionArray,crondallowdenyFileOwnerArray=crondallowdenyFileOwnerArray,sshdIfEnabled=sshdIfEnabled,sshdConfigFilePermission=sshdConfigFilePermission,sshdIfDisableX11forwarding=sshdIfDisableX11forwarding,sshdIfSetMaxAuthTries=sshdIfSetMaxAuthTries,sshdIfEnableIgnoreRhosts=sshdIfEnableIgnoreRhosts,sshdIfDisableHostbasedAuthentication=sshdIfDisableHostbasedAuthentication,sshdIfDisablePermitRootLogin=sshdIfDisablePermitRootLogin,sshdIfDisablePermitEmptyPasswords=sshdIfDisablePermitEmptyPasswords,sshdIfDisablePermitUserEnvironment=sshdIfDisablePermitUserEnvironment,sshdIfSpecificMACs=sshdIfSpecificMACs,sshdIfSetClientAliveInterval=sshdIfSetClientAliveInterval,sshdIfSetLoginGraceTime=sshdIfSetLoginGraceTime,pamPwqualityconfIfExist=pamPwqualityconfIfExist,pamIfSetMinlen=pamIfSetMinlen,pamIfSetMinclass=pamIfSetMinclass,sshdSetedLockAndUnlockTimeFiles=sshdSetedLockAndUnlockTimeFiles,sshdNotSetedLockAndUnlockTimeFiles=sshdNotSetedLockAndUnlockTimeFiles,sshdPamdFileArray=sshdPamdFileArray,sshdPamdFileReuseLimitArray=sshdPamdFileReuseLimitArray,sshdPamdFileIfSetSha512Array=sshdPamdFileIfSetSha512Array,accountPassMaxDays=accountPassMaxDays,accountPassMinDays=accountPassMinDays,accountPassWarnDays=accountPassWarnDays,accountPassAutolockInactiveDays=accountPassAutolockInactiveDays,accountShouldUnloginArray=accountShouldUnloginArray,accountGIDOfRoot=accountGIDOfRoot,accountProfileFileArray=accountProfileFileArray,accountProfileTMOUTArray=accountProfileTMOUTArray,accountIfSetUsersCanAccessSuCommand=accountIfSetUsersCanAccessSuCommand,importantFilenameArray=importantFilenameArray,importantFilePermissionArray=importantFilePermissionArray,importantFileUidgidArray=importantFileUidgidArray,userIfSetPasswdOrArray=userIfSetPasswdOrArray,uid0OnlyRootOrArray=uid0OnlyRootOrArray,pathDirIfNotHasDot=pathDirIfNotHasDot,pathDirPermissionHasGWArray=pathDirPermissionHasGWArray,pathDirPermissionHasOWArray=pathDirPermissionHasOWArray,pathDirOwnerIsNotRootArray=pathDirOwnerIsNotRootArray,pathDirDoesNotExistOrNotDirArray=pathDirDoesNotExistOrNotDirArray,userArray=userArray,userHomeDirIfExistArray=userHomeDirIfExistArray,userHomeDirPermissionArray=userHomeDirPermissionArray,userIfOwnTheirHomeDirArray=userIfOwnTheirHomeDirArray,userHomeDirIfHasGWorOWDotFileArray=userHomeDirIfHasGWorOWDotFileArray,userHomeDirIfHasOtherFileArray=userHomeDirIfHasOtherFileArray,groupNotExistInetcgroup=groupNotExistInetcgroup,usersIfHasUniqueUIDArray=usersIfHasUniqueUIDArray,groupsIfHasUniqueGIDArray=groupsIfHasUniqueGIDArray)
        # models.LinuxCheckRes.objects.get_or_create(scanTime=scanTime,osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList,ck_tmpIfSeparate=ck_tmpIfSeparate,ck_tmpIfNoexec=ck_tmpIfNoexec,ck_tmpIfNosuid=ck_tmpIfNosuid,ck_grubcfgPermissionLE600=ck_grubcfgPermissionLE600,ck_grubcfgIfSetPasswd=ck_grubcfgIfSetPasswd,ck_singleUserModeIfNeedAuth=ck_singleUserModeIfNeedAuth,ck_selinuxStateIfEnforcing=ck_selinuxStateIfEnforcing,ck_selinuxPolicyIfConfigured=ck_selinuxPolicyIfConfigured,ck_timeSyncServerIfConfigured=ck_timeSyncServerIfConfigured,ck_x11windowIfNotInstalled=ck_x11windowIfNotInstalled,ck_hostsAllowFilePermission=ck_hostsAllowFilePermission,ck_hostsAllowFileIfConfigured=ck_hostsAllowFileIfConfigured,ck_hostsDenyFilePermission=ck_hostsDenyFilePermission,ck_hostsDenyFileIfConfigured=ck_hostsDenyFileIfConfigured,ck_iptablesIfInstalled=ck_iptablesIfInstalled,ck_iptablesInputPolicyIfDrop=ck_iptablesInputPolicyIfDrop,ck_iptablesOutputPolicyIfDrop=ck_iptablesOutputPolicyIfDrop,ck_auditdIfEnabled=ck_auditdIfEnabled,ck_auditdIfSetMaxLogFile=ck_auditdIfSetMaxLogFile,ck_auditdIfSetMaxLogFileAction=ck_auditdIfSetMaxLogFileAction,ck_auditdIfSetSpaceLeftAction=ck_auditdIfSetSpaceLeftAction,ck_auditdIfSetNumLogs=ck_auditdIfSetNumLogs,ck_auditdIfCheckTimechange=ck_auditdIfCheckTimechange,ck_auditdRulesNotCheckedUserandgroupfile=ck_auditdRulesNotCheckedUserandgroupfile,ck_auditdRulesNotCheckedNetworkenv=ck_auditdRulesNotCheckedNetworkenv,ck_auditdRulesNotCheckedMACchange=ck_auditdRulesNotCheckedMACchange,ck_auditdRulesNotCheckedDACChangeSyscall=ck_auditdRulesNotCheckedDACChangeSyscall,ck_auditdRulesNotCheckedFileAccessAttemptSyscall=ck_auditdRulesNotCheckedFileAccessAttemptSyscall,ck_auditdRulesNotCheckedLoginoutEvents=ck_auditdRulesNotCheckedLoginoutEvents,ck_auditdRulesNotCheckedPrivilegedCommand=ck_auditdRulesNotCheckedPrivilegedCommand,ck_auditdRulesNotCheckedSudoerFile=ck_auditdRulesNotCheckedSudoerFile,ck_auditdRulesIfImmutable=ck_auditdRulesIfImmutable,ck_rsyslogIfEnabled=ck_rsyslogIfEnabled,ck_crondIfEnabled=ck_crondIfEnabled,ck_crondConfigFilePermissionArray=ck_crondConfigFilePermissionArray,ck_crondallowdenyFilePermissionArray=ck_crondallowdenyFilePermissionArray,ck_sshdConfigFilePermission=ck_sshdConfigFilePermission,ck_sshdIfDisableX11forwarding=ck_sshdIfDisableX11forwarding,ck_sshdIfSetMaxAuthTries=ck_sshdIfSetMaxAuthTries,ck_sshdIfEnableIgnoreRhosts=ck_sshdIfEnableIgnoreRhosts,ck_sshdIfDisableHostbasedAuthentication=ck_sshdIfDisableHostbasedAuthentication,ck_sshdIfDisablePermitRootLogin=ck_sshdIfDisablePermitRootLogin,ck_sshdIfDisablePermitEmptyPasswords=ck_sshdIfDisablePermitEmptyPasswords,ck_sshdIfDisablePermitUserEnvironment=ck_sshdIfDisablePermitUserEnvironment,ck_sshdIfSpecificMACs=ck_sshdIfSpecificMACs,ck_sshdIfSetClientAliveInterval=ck_sshdIfSetClientAliveInterval,ck_sshdIfSetLoginGraceTime=ck_sshdIfSetLoginGraceTime,ck_pamIfSetMinlen=ck_pamIfSetMinlen,ck_pamIfSetMinclass=ck_pamIfSetMinclass,ck_sshdNotSetedLockAndUnlockTimeFiles=ck_sshdNotSetedLockAndUnlockTimeFiles,ck_sshdPamdFileReuseLimitArray=ck_sshdPamdFileReuseLimitArray,ck_sshdPamdFileIfSetSha512Array=ck_sshdPamdFileIfSetSha512Array,ck_accountPassMaxDays=ck_accountPassMaxDays,ck_accountPassMinDays=ck_accountPassMinDays,ck_accountPassWarnDays=ck_accountPassWarnDays,ck_accountPassAutolockInactiveDays=ck_accountPassAutolockInactiveDays,ck_accountShouldUnloginArray=ck_accountShouldUnloginArray,ck_accountGIDOfRoot=ck_accountGIDOfRoot,ck_accountProfileTMOUTArray=ck_accountProfileTMOUTArray,ck_accountIfSetUsersCanAccessSuCommand=ck_accountIfSetUsersCanAccessSuCommand,ck_importantFilePermissionArray=ck_importantFilePermissionArray,ck_importantFileUidgidArray=ck_importantFileUidgidArray,ck_userIfSetPasswdOrArray=ck_userIfSetPasswdOrArray,ck_uid0OnlyRootOrArray=ck_uid0OnlyRootOrArray,ck_pathDirIfNotHasDot=ck_pathDirIfNotHasDot,ck_pathDirPermissionHasGWArray=ck_pathDirPermissionHasGWArray,ck_pathDirPermissionHasOWArray=ck_pathDirPermissionHasOWArray,ck_pathDirDoesNotExistOrNotDirArray=ck_pathDirDoesNotExistOrNotDirArray,ck_userHomeDirIfExistArray=ck_userHomeDirIfExistArray,ck_userHomeDirPermissionArray=ck_userHomeDirPermissionArray,ck_userIfOwnTheirHomeDirArray=ck_userIfOwnTheirHomeDirArray,ck_userHomeDirIfHasGWorOWDotFileArray=ck_userHomeDirIfHasGWorOWDotFileArray,ck_userHomeDirIfHasOtherFileArray=ck_userHomeDirIfHasOtherFileArray,ck_groupNotExistInetcgroup=ck_groupNotExistInetcgroup,ck_usersIfHasUniqueUIDArray=ck_usersIfHasUniqueUIDArray,ck_groupsIfHasUniqueGIDArray=ck_groupsIfHasUniqueGIDArray)
        # models.AllScanResRecord.objects.get_or_create(scanTime=scanTime,scanType="OS",osVersion=osVersion,hostname=hostname,macaddr=macaddr,ipList=ipList)
        # return HttpResponse("Success.")
    else:
        return HttpResponse("0oops,something is wrong")