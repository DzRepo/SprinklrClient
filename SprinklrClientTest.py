import SprinklrClient as sc
import json
from easysettings import EasySettings
import sys
from datetime import timezone
import datetime
import time
import webbrowser as wb
import logging

# from datetime import datetime
import logging

client = None
settings = None

def authorize(api_key, redirect_uri):
    global client
    url = client.authorize(api_key, redirect_uri)
    wb.open(url, new=2)

def get_access_token(code):
    logging.info("get_access_token called")
    global client
    global settings
    secret = settings.get('secret')
    redirect = settings.get('redirect')

    success = client.get_access_token(secret=secret, redirect_uri=redirect, code=code)

    if not success:
        logging.error(client.status_message)
        if client.status_message is not None:
            j_result = json.loads(client.status_message)
            print("Error: ", json.dumps(j_result, indent=4, sort_keys=True))

def refresh_access_token():
    global client
    secret = settings.get('secret')
    redirect = settings.get('redirect')
    code = settings.get('code')

    success = client.get_access_token(secret=secret, redirect_uri=redirect, code=code)

    if success:
        print("Encoding:", client.encoding)
        print("Last Status Code:", client.last_status_code)
        print("Access Token:", client.access_token)
        print("Refresh Token:", client.refresh_token)
    else:
        logging.error(client.status_message)
        if client.status_message is not None:
            j_result = json.loads(client.status_message)
            print("Error: ", json.dumps(j_result, indent=4, sort_keys=True))

def get_all_dashboards():
    global client
    process_response(client.request_all_dashboards())

def get_dashboard_by_name(dashboard_name):
    global client
    process_response(client.request_dashboard_by_name(dashboard_name))

def get_dashboard_stream(dashboard_id, start, rows):
    global client
    process_response(client.request_dashboard_stream(dashboard_id=dashboard_id, start=start, rows=rows))

def get_listening_topics():
    global client
    process_response(client.get_listening_topics())

def get_listening_stream(filter_value, since_time, until_time, timezone_offset=14400000, time_field="SN_CREATED_TIME",
                         details="STREAM", dimension="TOPIC", metric="MENTIONS", trend_aggregation_period=None, start=1,
                         rows=100, echo_request=False, tag=None, sort_key=None, message_format_options=None):
    global client

    process_response(client.get_listening_stream(filter_value, since_time, until_time, timezone_offset, time_field,
                                          details, dimension, metric, trend_aggregation_period, start,
                                          rows, echo_request, tag, sort_key, message_format_options))

def get_resources(types):
    global client
    process_response(client.get_resources(types))

def get_partner_accounts():
    global client
    process_response(client.get_partner_accounts())

def get_partner_campaigns():
    global client
    process_response(client.get_partner_campaigns())

def get_partner_account_groups():
    global client
    process_response(client.get_partner_campaigns())

def get_partner_users():
    global client
    process_response(client.get_partner_users())

def get_client_users():
    global client
    process_response(client.get_client_queues())

def get_clients():
    global client
    process_response(client.get_clients())

def get_client_url_shortners():
    global client
    process_response(client.get_client_url_shortners())

def get_inbound_custom_fields():
    global client
    process_response(client.get_inbound_custom_fields())

def get_outbound_custom_fields():
    global client
    process_response(client.get_outbound_custom_fields())

def get_profile_custom_fields():
    global client
    process_response(client.get_profile_custom_fields())

def get_media_asset_custom_fields():
    global client
    process_response(client.get_media_asset_custom_fields())

def get_account_custom_fields():
    global client
    process_response(client.get_account_custom_fields())

def get_um_statuses():
    global client
    process_response(client.get_um_statuses())

def get_um_priorities():
    global client
    process_response(client.get_um_priorities())

def get_accessible_users():
    global client
    process_response(client.get_accessible_users())

def get_approval_paths():
    global client
    process_response(client.get_approval_paths())

def get_partner_queues():
    global client
    process_response(client.get_partner_queues())

def get_client_queues():
    global client
    process_response(client.get_client_queues())

def get_partner_profile_lists():
    global client
    process_response(client.get_partner_profile_lists())

def get_client_profile_lists():
    global client
    success = client.get_client_profile_lists()
    process_response(success)

def get_macros():
    global client
    process_response(client.get_macros())

def get_permissions():
    global client
    process_response(client.get_permissions())

def get_user_groups():
    global client
    process_response(client.get_user_groups())

def date_time_toepoch(date_time : datetime.datetime):
    return datetime_toepoch(date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute)

def datetime_toepoch(year : int, month : int, day : int, hour=0, minute=0):
    return int(float(time.mktime(datetime.datetime(year, month, day, hour,minute).timetuple())) * 1000)

def datetime_fromepoch(epoch):
    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))

def get_report_data_location_analyisis():
    global client
    rb = sc.ReportBuilder()

    rb.set_engine("LISTENING")
    rb.set_name("SPRINKSIGHTS")
    
    rb.set_start_time(datetime_toepoch(2018, 9, 6, 0, 0))
    rb.set_end_time(datetime_toepoch(2019, 9, 5, 11, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(50)
    rb.set_page(0)

    rb.add_column("Avg. of Experience Score", "NLP_INSIGHT_POLARITY_SCORE","AVG")
    rb.add_column("Avg. of Star Rating","STAR_RATING","AVG")
    rb.add_column("Insights","NLP_DOC_INSIGHT_COUNT","SUM")

    rb.add_group_by("Location", "LOCATION_IDS", "FIELD")

    rb.add_filter("IN", "LOCATION_CUSTOM_PROPERTY", ["Hyatt"], {
                        "srcType": "CUSTOM",
                        "fieldName": "5ce45bf5e4b0a645c7d3e18a"
                    })
    rb.add_filter("IN", "HIERARCHY_ID", ["5c484387e4b0e6a8e58d17b2"],{
                        "contentType": "DB_FILTER",
                        "ASSET_CLASS": "INTEL_LOCATION",
                        "withAssetLevel": True,
                        "withDimension": True
                    })

    if rb.build_report_request():
        process_response(client.report_query(rb.request))
    else:
        print("Error building request:", rb.last_error)

def get_report_user_audit():
    global client
    rb = sc.ReportBuilder()

    rb.set_engine("PLATFORM")
    rb.set_name("USER_AVAILABILITY_REPORT")
    
    rb.set_start_time(datetime_toepoch(2019, 12, 1, 0, 0))
    rb.set_end_time(datetime_toepoch(2019, 12, 13, 11, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(100)
    rb.set_page(0)
    
    # one_day_details = 
    rb.add_group_by("Date", "ACTION_TIME", "FIELD", {"interval": "1m"} )
    rb.add_group_by("User", "USER_ID", "FIELD")
#    rb.add_group_by("User Group", "USER_GROUP_ID", "FIELD")
    rb.add_group_by("Status", "LOGIN_CURRENT_STATUS", "FIELD")
    rb.add_group_by("IP Address", "IP_ADDRESS", "FIELD")

    rb.add_column("Session Length", "loggedInSession","SUM")

    if rb.build_report_request():
        process_response(client.report_query(rb.request))
    else:
        print("Error building request:", rb.last_error)

def get_report_data_attibutes():
    global client
    rb = sc.ReportBuilder()

    rb.set_engine("LISTENING")
    rb.set_name("SPRINKSIGHTS")
    
    rb.set_start_time(datetime_toepoch(2018, 9, 6, 0, 0))
    rb.set_end_time(datetime_toepoch(2019, 9, 5, 11, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(50)
    rb.set_page(0)

    rb.add_column("Average of Experience Score","NLP_INSIGHT_POLARITY_SCORE","AVG")

    rb.add_group_by("Category", "LTS_OC", "FIELD")
    rb.add_group_by("Location", "LOCATION_IDS","FIELD")

    rb.add_filter("IN", "LOCATION_CUSTOM_PROPERTY", ["Hyatt"], {
                        "srcType": "CUSTOM",
                        "fieldName": "5ce45bf5e4b0a645c7d3e18a"
                    })
    rb.add_filter("IN", "HIERARCHY_ID", ["5c484387e4b0e6a8e58d17b2"],{
                        "contentType": "DB_FILTER",
                        "ASSET_CLASS": "INTEL_LOCATION",
                        "withAssetLevel": True,
                        "withDimension": True
                    })

    if rb.build_report_request():
        process_response(client.report_query(rb.request))
    else:
        print("Error building request:", rb.last_error)

def get_report_data_subject_categories():
    global client
    rb = sc.ReportBuilder()

    rb.set_engine("LISTENING")
    rb.set_name("SPRINKSIGHTS")
    
    rb.set_start_time(datetime_toepoch(2018, 9, 6, 0, 0))
    rb.set_end_time(datetime_toepoch(2019, 9, 15, 12, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(50)
    rb.set_page(0)

    rb.add_column("Avg. of Experience Score", "NLP_INSIGHT_POLARITY_SCORE","AVG")

    rb.add_group_by("LTS_NOC", "LTS_NOC", "FIELD")
    rb.add_group_by("Location IDs", "LOCATION_IDS", "FIELD")

    rb.add_filter("IN", "LOCATION_CUSTOM_PROPERTY", ["Hyatt"], {
                        "srcType": "CUSTOM",
                        "fieldName": "5ce45bf5e4b0a645c7d3e18a"
                    })
    rb.add_filter("IN", "HIERARCHY_ID", ["5c484387e4b0e6a8e58d17b2"],{
                        "contentType": "DB_FILTER",
                        "ASSET_CLASS": "INTEL_LOCATION",
                        "withAssetLevel": True,
                        "withDimension": True
                    })

    if rb.build_report_request():
        process_response(client.report_query(rb.request))
    else:
        print("Error building request:", rb.last_error)

def get_report_data_reviews():
    global client
    rb = sc.ReportBuilder()

    rb.set_engine("LISTENING")
    rb.set_name("SPRINKSIGHTS")
    
    rb.set_start_time(datetime_toepoch(2018, 9, 6, 0, 0))
    rb.set_end_time(datetime_toepoch(2019, 9, 15, 12, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(10)
    rb.set_page(0)

    rb.add_column("Avg. of Experience Score", "NLP_DOC_POLARITY_SCORE","AVG")
    
    rb.add_group_by("Message", "ES_MESSAGE_ID","FIELD")
    rb.add_group_by("Location IDs", "LOCATION_IDS", "FIELD", {"missing": 0})
    rb.add_group_by("Created Time", "SN_CREATED_TIME", "DATE_HISTOGRAM", {
                                                "interval": "1M"
                                            })
    rb.add_group_by("Star Rating", "STAR_RATING", "FIELD", {"missing": 0})
    
    rb.add_filter("IN", "HIERARCHY_ID", ["5c484387e4b0e6a8e58d17b2"],{
                        "contentType": "DB_FILTER",
                        "ASSET_CLASS": "INTEL_LOCATION",
                        "withAssetLevel": True,
                        "withDimension": True
                    })

    if rb.build_report_request():
        print(json.dumps(rb.request, sort_keys=False, indent=4))
        process_response(client.report_query(rb.request))
    else:
        print("Error building request:", rb.last_error)


def get_report_metrics(report_engine, report_name):
    global client
    process_response(client.get_report_metrics(report_engine, report_name))

def get_webhook_types():
    global client
    process_response(client.get_webhook_types())
 

def asset_search_one():
#    global client
#    client.asset_search()
    return

def asset_search_two():
    return

def asset_search_three():
    return

def create_case():
    global client
    case = sc.CaseCreate()
    now_as_epoch = date_time_toepoch(datetime.datetime.now())
    
    workflow = case.Workflow()
    workflow.add_queue(case.Workflow.Queue(123, now_as_epoch))
    workflow.assignment = case.Workflow.Assignment("123", "USER", 123, now_as_epoch)
    workflow.modified_time = now_as_epoch
    workflow.campaign_id = 123 # campaign ID ?
    space_workflow = case.Workflow.SpaceWorkflow("123", now_as_epoch)
    space_workflow.add_queue("123", now_as_epoch)
    space_workflow.add_custom_field("CustomField1", "custom_field_1")
    workflow.add_space_workflow(space_workflow)
    
    case_attachment = case.Attachment("IMAGE")
    case_attachment.add_option(case.Attachment.Attachment_Option("TWITTER", 1))
    
    case.id = "12345"
    case.case_number = 12345
    case.subject = "A case Opened via API"
    case.description = "Case Created on " + datetime.datetime.now().strftime("%c")
    case.version = "1"
    case.status = "Open"
    case.priority = "High" # ?
    case.case_type = "Problem"
    case.external_case = case.External_Case(12345, "12345", "salesforce", None, now_as_epoch, now_as_epoch)
    case.contact = case.Contact(123, "Ariel Tritan")
    case.attachment = case_attachment
    case.due_date = now_as_epoch + 10000
    case.summary = "A new case created via API"
    case.created_time = now_as_epoch
    case.modified_time = now_as_epoch
    case.first_message_id = 123 
    case.workflow = workflow

    client.create_case_v2(case)


def get_case_by_number(case_number):
    global client
    if client.get_case_by_number(case_number):
        print(json.dumps(client.result, sort_keys=True, indent=4))
    else:
        print(client.status_message)   

def get_message_by_id_and_source(message_id, source_type):
    global client
    if client.get_message_by_id_and_source(message_id, source_type):
        print(json.dumps(client.result, sort_keys=True, indent=4))
    else:
        print(client.status_message)   

def get_case_messages(case_id):
    global client
    if client.get_case_associated_messages(case_id):
        print(json.dumps(client.result, sort_keys=True, indent=4))
    else:
        print(client.status_message)

def get_user():
    global client
    process_response(client.get_user())

def get_user_by_id(user_id):
    global client
    process_response(client.get_user_by_id(user_id))

# def search_entity(entity_type, filter, sort, key, order='ASC')

def process_response(success):
    try:
        logging.debug("Success:" + str(success))
        if success:
            if client.result is None:
                logging.debug("No Results")
                logging.debug("Status Message:" + client.status_message)
                print(client.status_message)
            else:
                logging.debug("Result Type:" + str(type(client.result)))
                #logging.debug("Result:" + str(client.result))
                if type(client.result) is dict or type(client.result) is list:
                    print(json.dumps(client.result, sort_keys=False, indent=4))
                else:
                    print(client.result)
        else:
            if client.status_message is None:
                if type(client.result) is dict:
                    logging.debug("Result is a dictionary")
                    print(json.dumps(client.result, sort_keys=False, indent=4))
                else:
                    print(client.result)
            else: 
                print(client.status_message)
    except Exception as ex:
        logging.error(str(ex))
        print("Error: " + str(ex))


def print_usage():
        print("Usage:")
        print("SprinklrClientTest Authorize {apikey} {redirect_uri}")
        print("                   AssetSearch [One | Two | Three]")
        print("                   CreateCase")
        print("                   GetAccessToken {apikey} {secret} {code} {redirect uri}")
        print("                   GetAccessibleUsers")
        print("                   GetAccountCustomFields")
        print("                   GetAllDashboards")
        print("                   GetCaseByNumber {case_number}")
        print("                   GetCaseMessagesById {case_id}")
        print("                   GetClients")
        print("                   GetClientProfileLists")
        print("                   GetClientUrlShortners")
        print("                   GetClientUsers")
        print("                   GetDashboardByName {name}")
        print("                   GetDashboardStream {stream_id} {start} {rows} [{echo request} (True or False)]")
        print("                   GetInboundCustomFields")
        print("                   GetListeningTopics")
        print("                   GetListeningStream {id} {sinceTime} {untilTime}")
        print("                   GetMacros")
        print("                   GetMediaAssetCustomFields")
        print("                   GetMessageByIdAndSource {message_id} [ACCOUNT | PERSISTENT_SEARCH | LISTENING | BENCHMARKING | AUDIENCE | AUDIENCE_STUDY]}")
        print("                   GetOutboundCustomFields")
        print("                   GetPartnerAccountGroups")
        print("                   GetPartnerAccounts")
        print("                   GetPartnerCampaigns")
        print("                   GetPartnerUsers")
        print("                   GetPermissions")
        print("                   GetProfileCustomFields")
        print("                   GetReport LOCATION | CATEGORIES | ATTRIBUTES | REVIEWS | AUDIT")
        print("                   GetReportMetrics {Report_Engine} {Report_Type}")
        print("                   GetResources {resource type}")
        print("                   GetUMPriorities")
        print("                   GetUMStatuses")
        print("                   GetUser")
        print("                   GetUserById {User_Id}")
        print("                   GetUserGroups")
        print("                   GetWebhookTypes")
        print("                   RefreshAccessToken")

def main():
    global settings
    global client

    try:
        logging.basicConfig(filename='SprinklrClient.log', level=logging.DEBUG)
        logging.debug("Starting SprinklrClientTest with " + str(len(sys.argv) - 1) + " actual parameters")

        settings = EasySettings("Sprinklr.conf")

        key = settings.get('key')
        access_token = settings.get('access_token')
        client = sc.SprinklrClient(key=key, access_token=access_token)

        if len(sys.argv) > 1:
            command = str(sys.argv[1]).upper()

            if command == 'AUTHORIZE':
                if len(sys.argv) != 4:
                    print("Invalid command line - Usage: SprinklrClientTest Authorize {apikey} {redirect_uri}")
                else:
                    key = sys.argv[2]
                    redirect_uri = sys.argv[3]
                    client = sc.SprinklrClient(key)
                    authorize(key, redirect_uri)
            elif command == 'ASSETSEARCH':
                if len(sys.argv) != 3:
                    print("Invalid command line - Usage: SprinklrClientTest AssetSearch [One | Two | Three]")
                else:
                    if sys.argv[2].upper() == "ONE":
                        asset_search_one()
                    elif sys.argv[2].upper() == "TWO":
                        asset_search_two()
                    elif sys.argv[2].upper() == "THREE":
                        asset_search_three()
                    else:
                        print("Invalid Asset Search Option passed:", sys.argv[2])
            elif command == "CREATECASE":
                create_case()
            elif command == 'GETALLDASHBOARDS':
                get_all_dashboards()
            elif command == 'GETACCESSTOKEN':
                if len(sys.argv) != 6:
                    print(
                        "Invalid command line - Usage: SprinklrClientTest GetAccessToken {apikey} {secret} "
                        "{code} {redirect URI}")
                else:
                    key = sys.argv[2]
                    secret = sys.argv[3]
                    code = sys.argv[4]
                    redirect = sys.argv[5]

                    client = sc.SprinklrClient(key)
                    success = client.get_access_token(secret=secret, code=code, redirect_uri=redirect)

                    if success:
                        settings.set('access_token', client.access_token)
                        settings.set('refresh_token', client.refresh_token)
                        settings.set('redirect_uri', redirect)
                        settings.set('key', key)
                        settings.set('secret', secret)
                        settings.save()
                        print("Success")
                    else:
                        print(client.result)

                    key = settings.get('key')
                    access_token = settings.get('access_token')
                    client = sc.SprinklrClient(key=key, access_token=access_token)
            elif command == 'GETACCESSIBLEUSERS':
                get_accessible_users()
            elif command == 'GETACCOUNTCUSTOMFIELDS':
                get_account_custom_fields()
            elif command == "GETCASEBYNUMBER":
                get_case_by_number(sys.argv[2])
            elif command == "GETCASEMESSAGESBYID":
                get_case_messages(sys.argv[2])
            elif command == "GETCLIENTS":
                get_clients()
            elif command == 'GETCLIENTPROFILELISTS':
                get_client_profile_lists()
            elif command == "GETCLIENTURLSHORTNERS":
                get_client_url_shortners()
            elif command == 'GETCLIENTUSERS':
                get_client_users()
            elif command == 'GETDASHBOARDBYNAME':
                if len(sys.argv) != 3:
                    print("Invalid command line - Usage: SprinklrClientTest GetDashboardByName {name}")
                else:
                    get_dashboard_by_name(sys.argv[2])
            elif command == 'GETDASHBOARDSTREAM':
                get_dashboard_stream(sys.argv[2], sys.argv[3], sys.argv[4])
            elif command == 'GETINBOUNDCUSTOMFIELDS':
                get_inbound_custom_fields()
            elif command == 'GETLISTENINGTOPICS':
                get_listening_topics()
            elif command == 'GETLISTENINGSTREAM':
                if len(sys.argv) == 5:
                    get_listening_stream(sys.argv[2], sys.argv[3], sys.argv[4])
                elif len(sys.argv) == 6:
                    get_listening_stream(sys.argv[2], sys.argv[3], sys.argv[4], echo_request=sys.argv[5])
            elif command == 'GETMACROS':
                get_macros()
            elif command == 'GETMEDIAASSETCUSTOMFIELDS':
                get_media_asset_custom_fields()
            elif command == 'GETMESSAGEBYIDANDSOURCE':
                get_message_by_id_and_source(sys.argv[2], sys.argv[3])
            elif command == 'GETOUTBOUNDCUSTOMFIELDS':
                get_outbound_custom_fields()
            elif command == 'GETPARTNERACCOUNTGROUPS':
                get_partner_account_groups()
            elif command == 'GETPARTNERACCOUNTS':
                get_partner_accounts()
            elif command == 'GETPARTNERCAMPAIGNS':
                get_partner_campaigns()
            elif command == 'GETPARTNERUSERS':
                get_partner_users()
            elif command == 'GETPERMISSIONS':
                get_permissions()
            elif command == 'GETPROFILECUSTOMFIELDS':
                get_profile_custom_fields()
            elif command == "GETREPORT":
                if sys.argv[2].upper() == "LOCATION":
                    get_report_data_location_analyisis()
                elif sys.argv[2].upper() == "CATEGORIES":
                    get_report_data_subject_categories()
                elif sys.argv[2].upper() == "ATTRIBUTES":
                    get_report_data_attibutes() 
                elif sys.argv[2].upper() == "REVIEWS":
                    get_report_data_reviews()
                elif sys.argv[2].upper() == "AUDIT":
                    get_report_user_audit()
                else:
                    print("Report not found")
            elif command == "GETREPORTMETRICS":
                get_report_metrics(sys.argv[2], sys.argv[3])
            elif command == 'GETRESOURCES':
                get_resources(sys.argv[2])
            elif command == 'GETUSER':
                get_user()
            elif command == 'GETUSERBYID':
                get_user_by_id(sys.argv[2])
            elif command == 'GETUMPRIORITIES':
                get_um_priorities()
            elif command == 'GETUMSTATUSES':
                get_um_statuses()
            elif command == "GETUSERGROUPS":
                get_user_groups()
            elif command == "GETWEBHOOKTYPES":
                get_webhook_types()
            elif command == "REFRESHACCESSTOKEN":
                key = settings.get('key')
                secret = settings.get('secret')
                redirect = settings.get('redirect_uri')
                refresh_access_token = settings.get('refresh_token')

                client = sc.SprinklrClient(key)

                success = client.refresh_access_token(key, secret, redirect, refresh_access_token)

                if success:
                    settings.set('access_token', client.access_token)
                    settings.set('refresh_token', client.refresh_token)
                    settings.set('redirect_uri', redirect)
                    settings.set('key', key)
                    settings.set('secret', secret)
                    settings.save()
                    print("Success")
                else:
                    print(client.result)
            else:
                print_usage()
        else:
            print_usage()
    except Exception as ex:
        print("Error:" + str(ex))
        print_usage()
        
if __name__ == "__main__":
    main()
