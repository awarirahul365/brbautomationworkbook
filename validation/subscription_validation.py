from services.auth_service import AuthService
from services.subscription_service import SubscriptionService
from services.support_service import SupportService
import logging,asyncio

class Subvalidation:

    @staticmethod
    async def preview_support_function(subid:str,azrnum:str,cred_key:str):
        try:
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
        except Exception as e:
            logging.error(f"Error with preview_support_function {e}")
    
    @staticmethod
    async def get_subscription_function(subid:str):
        credential_list=AuthService.get_credential_keys()
        res=await asyncio.gather(
            *(asyncio.create_task(
                Subvalidation.sublistfunction(cred)
            )for cred in credential_list)
        )
        #logging.info(f"Res answers is {res}")
        logging.info(f"Length of sublist {len(res[0]['sublist'])}")
        logging.info(f"Length of sublist1 {len(res[1]['sublist'])}")
        if subid in res[0]['sublist']:
            present=True
            cred_key=res[0]['Credential_key']
        elif subid in res[1]['sublist']:
            present=True
            cred_key=res[1]['Credential_key']
        else:
            present=None
            cred_key=None
        logging.info(f"Check present {present} {cred_key}")
        return present,cred_key
    
    @staticmethod
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