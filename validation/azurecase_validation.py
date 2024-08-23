from services.auth_service import AuthService
from azure.mgmt.support.aio import MicrosoftSupport
import logging,asyncio
class Azurecasevalidation:

    @staticmethod
    async def check_azure_casenum_function(subid:str,azrnum:str,cred_key:str):
        try:
            credential_azrnum,cloud=AuthService.get_credential(credential_key=cred_key)
            async with credential_azrnum:
                client_azrnum=MicrosoftSupport(
                    credential=credential_azrnum,
                    subscription_id=subid,
                    base_url="https://management.azure.com"
                )
                resp=client_azrnum.support_tickets.list(
                    top=10,
                    filter="status eq 'Open'"
                )
                azrnum_present=False
                async for i in resp:
                    if i.support_ticket_id == azrnum :
                        azrnum_present=True
                        break
                logging.info("Azure Case Number is present")
                return azrnum_present
        except Exception as e:
            logging.info(f" Azure case number not present in Open ticket list of first 10 {e}")
            return azrnum_present
        finally:
            await credential_azrnum.close()
            await client_azrnum.close()

