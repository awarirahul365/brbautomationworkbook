import azure.functions as func
import logging
from services.auth_service import AuthService
from services.subscription_service import SubscriptionService
from services.support_service import SupportService
import asyncio
import json
import itertools
import os
from simple_colors import *
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

async def sublistfunction(cred:str):
    credential,cloud=AuthService.get_credential(cred)
    try:
        async with credential:
            sublistinput=await SubscriptionService.subscription_list(credentials=credential,cloud=cloud)
            sublist=SubscriptionService.filter_ids(sublistinput)
        res_dict_sublist={
            'Credential_key':cred,
            'sublist':sublist
        }
        return res_dict_sublist
    except Exception as e:
        logging.error(f"Failed to fetch subscription list {e}")
        return None
    
async def get_subscription_function(subid:str):
    credential_list=AuthService.get_credential_keys()
    res=await asyncio.gather(
        *(asyncio.create_task(
            sublistfunction(cred)
        )for cred in credential_list)
    )
    present=False
    cred_key=None
    for i in res:
        if subid in i['sublist']:
            present=True
            cred_key=i['Credential_key']
            break 
    return present,cred_key

async def preview_support_function(subid:str,azrnum:str,cred_key:str):
    result=await SupportService.preview_support_ticket_details(
        credential_key=cred_key,
        subid=subid,
        azrnum=azrnum
    )
    
    dict_ans={
        'Result':result,
        'Credential_Key':cred_key
    }
    return dict_ans
@app.route(route="http_trigger_support_ticket")
async def http_trigger_support_ticket(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    subid=req.params.get('subid')
    azrnum=req.params.get('azrnum')
    fname=req.params.get('fname')
    lname=req.params.get('lname')
    emailprimary=req.params.get('e1')
    mimid=req.params.get('mimid')
    meetlink=req.params.get('mlink')
    incdesp=req.params.get('incdesp')
    custimp=req.params.get('custimp')
    state=req.params.get('state')
    additionalemail=req.params.get('e2')
    #email3=req.params.get('e3')
    sub_present,cred_key=await get_subscription_function(subid=subid)
    logging.info(f"sub_present {sub_present}")
    logging.info(f"cred_key present {cred_key}")
    if sub_present == True:
        previewticketdetails=await preview_support_function(subid,azrnum,cred_key)
        if state == "start":
            if previewticketdetails['Result'] is not None:
                #res=previewticketdetails
                #ticketdetails=previewticketdetails['Result']
                description_new=[
                    previewticketdetails['Result']['description'],
                    "Title: SAP MIM BRB - Critical Support Ticket | MIM # | Sev-A SR#",
                    "Your presence has been requested in the following MIM Bridge room:",
                    "Incident Description: ",
                    incdesp,
                    "SAP MIM ID: ",
                    mimid,
                    "Approved By: SAP MIM team",
                    "Major Incident for: ECS",
                    "Customer Imapcted: ",
                    custimp,
                    "Meeting Link: ",
                    meetlink,
                    "Parent support ticket",
                    azrnum]
                desp_content="\n\n".join(description_new)
                print(desp_content)
                createbrbticket=await SupportService.create_support_ticket_function(
                    ticketdetails=previewticketdetails['Result'],
                    desp_content=desp_content,
                    fname=fname,
                    lname=lname,
                    emailprimary=emailprimary,
                    additionalemail=additionalemail
                )
                if createbrbticket==1:
                    res="Ticket Created Please check the mail"
                #print(json.loads(previewticketdetails))
            else:
                res="Ticket Not Found"
        else:
            res="Input incomplete or check the inputs again"
    else:
        res="Subscription Not present"

    return func.HttpResponse(
             str(res),
             status_code=200
        )