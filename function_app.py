import azure.functions as func
import logging
from services.support_service import SupportService
from validation.subscription_validation import Subvalidation
from validation.azurecase_validation import Azurecasevalidation
from simple_colors import *
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

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
    logging.info(f"Additionalmailvalue {additionalemail}")
    logging.info(f"Subscriptionits {subid}")
    logging.info(f"Azurecasenum {azrnum}")
    sub_present,cred_key=await Subvalidation.get_subscription_function(subid=subid)
    azucase_present=await Azurecasevalidation.check_azure_casenum_function(
        subid=subid,
        azrnum=azrnum,
        cred_key=cred_key
    )
    logging.info(f"sub_present {sub_present}")
    logging.info(f"cred_key present {cred_key}")
    logging.info(f"azucase_present {azucase_present}")
    if sub_present == True and azucase_present == True:
        previewticketdetails=await Subvalidation.preview_support_function(subid=subid,azrnum=azrnum,cred_key=cred_key)
        if state == "started":
            if previewticketdetails['Result'] is not None:
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
                logging.info(f"Ticket status {createbrbticket}")
                if createbrbticket=="Succeeded":
                    res="Ticket Created Please check the mail"
                else:
                    res="Failed to create ticket check the parameters"
                #print(json.loads(previewticketdetails))
            else:
                res="Ticket Not Found"
        elif state == "reset parameter":
            res="Click Create Button enabled , fill in the parameters and click on create"
        else:
            res="Input incomplete or check the inputs again"
    else:
        res="Please check the subscription and Azure Case Number Again"

    return func.HttpResponse(
             str(res),
             status_code=200
        )