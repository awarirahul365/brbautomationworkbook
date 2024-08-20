from services.auth_service import AuthService
from azure.mgmt.support.aio import MicrosoftSupport
import logging
import os
from datetime import datetime
class SupportService:
    
    @staticmethod
    async def preview_support_ticket_details(credential_key,subid,azrnum):
        credential,cloud=AuthService.get_credential(credential_key)
        try:
            async with credential:
                try:
                    _client=MicrosoftSupport(
                        credential=credential,
                        subscription_id=subid,
                        base_url="https://management.azure.com"
                    )
                    response=_client.support_tickets.list(
                        top=10,
                        filter="status eq 'Open'"
                    )
                    payload={}
                    async for i in response:
                        if i.support_ticket_id == azrnum:
                            contactdetails=i.contact_details
                            description=i.description
                            problemClassificationId=i.problem_classification_id
                            serviceId=i.service_id
                            severity=i.severity
                            title=i.title
                            diag=i.advanced_diagnostic_consent
                            payload={
                                "country": contactdetails.country,
                                "firstName": contactdetails.first_name,
                                "lastName": contactdetails.last_name,
                                "preferredContactMethod": contactdetails.preferred_contact_method,
                                "preferredSupportLanguage": contactdetails.preferred_support_language,
                                "preferredTimeZone": contactdetails.preferred_time_zone,
                                "primaryEmailAddress": contactdetails.primary_email_address,
                                "description":description,
                                "problemClassificationId":problemClassificationId,
                                "serviceId":serviceId,
                                "severity":severity,
                                "title":title,
                                "advanced_diagnostic_consent":diag
                            }
                            break
                    return payload
                except Exception as e:
                    logging.error(f"Ticket Not present {e}")
                    return {}
                finally:
                    await _client.close()
        except Exception as e:
            logging.error(f"Error with support_service{e}")
            return None

    @staticmethod  
    async def create_support_ticket_function(
            ticketdetails,
            desp_content,
            fname:str,
            lname:str,
            emailprimary:str,
            additionalemail:str
    ):
        try:
            credential_brb,cloud_brb=AuthService.get_credential(credential_key=os.getenv("Credbrbkey"))
            async with credential_brb:
                clientdest=MicrosoftSupport(
                    credential=credential_brb,
                    subscription_id=os.getenv("brbsubid"),
                    base_url="https://management.azure.com"
                )
                current_datetime=datetime.now()
                date_string = current_datetime.strftime('%Y%m%d%H%M%S')
                ticketname="brbticket"+"_"+date_string
                payloadcreate={
                    "contactDetails":{
                    "country": ticketdetails['country'] if ticketdetails['country'] is not None else os.getenv("country_temp"),
                    "firstName": fname,
                    "lastName": lname,
                    "preferredContactMethod": os.getenv("contact_temp"),
                    "preferredSupportLanguage": ticketdetails['preferredSupportLanguage'] if ticketdetails['preferredSupportLanguage'] is not None else os.getenv("language_temp"),
                    "preferredTimeZone": ticketdetails['preferredTimeZone'] if ticketdetails['preferredTimeZone'] is not None else os.getenv("timezone"),
                    "primaryEmailAddress": emailprimary,
                },
                "description":desp_content,
                "problemClassificationId":ticketdetails['problemClassificationId'],
                "serviceId":ticketdetails['serviceId'],
                "severity":os.getenv('brbseverity'),
                "title":ticketdetails['title'],
                "advanced_diagnostic_consent":ticketdetails['advanced_diagnostic_consent']
                }
                if additionalemail is not None:
                    payloadcreate['contactDetails']['additionalEmailAddresses']=[additionalemail]
                logging.info(payloadcreate)
                response=await clientdest.support_tickets.begin_create(
                    support_ticket_name=ticketname,
                    create_support_ticket_parameters=payloadcreate
                )
                final_result=await response.result()
                return response.status()

        except Exception as e:
            logging.error(f"Error creating ticket View the details {e}")
            return 0
        finally:
            await clientdest.close()
          
        
        