import azure.functions as func
import logging
from services.auth_service import AuthService
from services.support_service import SupportService
import asyncio
import json
from itertools import chain
import os
from simple_colors import *
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

async def preview_support_function(subid:str,azrnum:str):
    credential_list=AuthService.get_credential_keys()
    result=await asyncio.gather(
        *(asyncio.create_task(
            SupportService.preview_support_ticket_details(cred,subid,azrnum)
        ) for cred in credential_list)
    )
    cred_key=None
    if len(result[0])!=0:
        ans=result[0]
        cred_key="CredSAPTenant"
    elif len(result[1])!=0:
        ans=result[1]
        cred_key="CredSharedTenant"
    else:
        ans=None
        cred_key=None
    dict_ans={
        'Result':ans,
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
    email2=req.params.get('e2')
    #email3=req.params.get('e3')
    previewticketdetails=await preview_support_function(subid,azrnum)
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
                "Approved By: SAP MIM team",
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
                emailprimary=emailprimary
            )
            if createbrbticket==1:
                res="Ticket Created Please check the mail"
            #print(json.loads(previewticketdetails))
        else:
            res="Ticket Not Found"
    else:
        res="Input incomplete or check the inputs again"
    return func.HttpResponse(
             str(res),
             status_code=200
        )