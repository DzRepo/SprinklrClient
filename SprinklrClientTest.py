#! /usr/bin/python3

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


def authorize(api_key, redirect_uri, path=None):
    global client
    url = client.authorize(api_key, redirect_uri, path)
    wb.open(url, new=2)


def fetch_access_token(code):
    logging.info("fetch_access_token called")
    global client
    global settings
    secret = settings.get('secret')
    redirect = settings.get('redirect')

    success = client.fetch_access_token(
        secret=secret, redirect_uri=redirect, code=code)

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

    success = client.fetch_access_token(
        secret=secret, redirect_uri=redirect, code=code)

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


def fetch_all_dashboards():
    global client
    process_response(client.fetch_all_dashboards())


def fetch_dashboard_by_name(dashboard_name):
    global client
    process_response(client.fetch_dashboard_by_name(dashboard_name))


def fetch_dashboard_stream(dashboard_id, start, rows):
    global client
    process_response(client.fetch_dashboard_stream(
        dashboard_id=dashboard_id, start=start, rows=rows))


def fetch_listening_topics():
    global client
    process_response(client.fetch_listening_topics())


def fetch_listening_stream(filter_value, since_time, until_time, timezone_offset=14400000,  time_field="SN_CREATED_TIME",
                           details="STREAM", dimension="TOPIC", metric="MENTIONS", trend_aggregation_period=None, start=1,
                           rows=100, echo_request=False, tag=None, sort_key=None, message_format_options=None):
    global client

    process_response(client.fetch_listening_stream(filter_value, since_time, until_time, timezone_offset, time_field,
                                                   details, dimension, metric, trend_aggregation_period, start,
                                                   rows, echo_request, tag, sort_key, message_format_options))


def fetch_resources(types):
    global client
    process_response(client.fetch_resources(types))


def fetch_partner_accounts():
    global client
    process_response(client.fetch_partner_accounts())


def fetch_partner_campaigns():
    global client
    process_response(client.fetch_partner_campaigns())


def fetch_partner_account_groups():
    global client
    process_response(client.fetch_partner_campaigns())


def fetch_partner_users():
    global client
    process_response(client.fetch_partner_users())


def fetch_client_users():
    global client
    process_response(client.fetch_client_queues())


def fetch_clients():
    global client
    process_response(client.fetch_clients())


def fetch_client_url_shortners():
    global client
    process_response(client.fetch_client_url_shortners())


def fetch_inbound_custom_fields():
    global client
    process_response(client.fetch_inbound_custom_fields())


def fetch_outbound_custom_fields():
    global client
    process_response(client.fetch_outbound_custom_fields())


def fetch_profile_custom_fields():
    global client
    process_response(client.fetch_profile_custom_fields())


def fetch_media_asset_custom_fields():
    global client
    process_response(client.fetch_media_asset_custom_fields())


def fetch_account_custom_fields():
    global client
    process_response(client.fetch_account_custom_fields())


def fetch_um_statuses():
    global client
    process_response(client.fetch_um_statuses())


def fetch_um_priorities():
    global client
    process_response(client.fetch_um_priorities())


def fetch_accessible_users():
    global client
    process_response(client.fetch_accessible_users())


def fetch_approval_paths():
    global client
    process_response(client.fetch_approval_paths())


def fetch_partner_queues():
    global client
    process_response(client.fetch_partner_queues())


def fetch_client_queues():
    global client
    process_response(client.fetch_client_queues())


def fetch_partner_profile_lists():
    global client
    process_response(client.fetch_partner_profile_lists())


def fetch_client_profile_lists():
    global client
    process_response(client.fetch_client_profile_lists())


def fetch_macros():
    global client
    process_response(client.fetch_macros())


def fetch_permissions():
    global client
    process_response(client.fetch_permissions())


def fetch_user_groups():
    global client
    process_response(client.fetch_user_groups())


def fetch_report_data_location_analyisis():
    global client
    rb = sc.ReportBuilder()

    rb.set_engine("LISTENING")
    rb.set_name("SPRINKSIGHTS")

    rb.set_start_time(datetime_toepoch(2018, 9, 6, 0, 0))
    rb.set_end_time(datetime_toepoch(2019, 9, 5, 11, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(50)
    rb.set_page(0)

    rb.add_column("Avg. of Experience Score",
                  "NLP_INSIGHT_POLARITY_SCORE", "AVG")
    rb.add_column("Avg. of Star Rating", "STAR_RATING", "AVG")
    rb.add_column("Insights", "NLP_DOC_INSIGHT_COUNT", "SUM")

    rb.add_group_by("Location", "LOCATION_IDS", "FIELD")

    rb.add_filter("IN", "LOCATION_CUSTOM_PROPERTY", ["Hyatt"], {
                        "srcType": "CUSTOM",
                        "fieldName": "5ce45bf5e4b0a645c7d3e18a"
    })
    rb.add_filter("IN", "HIERARCHY_ID", ["5c484387e4b0e6a8e58d17b2"], {
                        "contentType": "DB_FILTER",
                        "ASSET_CLASS": "INTEL_LOCATION",
                        "withAssetLevel": True,
                        "withDimension": True
    })

    if rb.build_report_request():
        process_response(client.fetch_report(rb.request))
    else:
        print("Error building request:", rb.last_error)


def fetch_report_user_audit():
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

    rb.add_group_by("Date", "ACTION_TIME", "FIELD", {"interval": "1D"})
    
    rb.add_group_by("User", "USER_ID", "FIELD")
#    rb.add_group_by("User Group", "USER_GROUP_ID", "FIELD")
    rb.add_group_by("Status", "LOGIN_CURRENT_STATUS", "FIELD")
    rb.add_group_by("IP Address", "IP_ADDRESS", "FIELD")

    rb.add_column("Session Length", "loggedInSession", "SUM")

    if rb.build_report_request():
        print(json.dumps(rb.request, sort_keys=False, indent=4))
        process_response(client.fetch_report(rb.request))
    else:
        print("Error building request:", rb.last_error)


def fetch_report_data_attibutes():
    global client
    rb = sc.ReportBuilder()

    rb.set_engine("LISTENING")
    rb.set_name("SPRINKSIGHTS")

    rb.set_start_time(datetime_toepoch(2018, 9, 6, 0, 0))
    rb.set_end_time(datetime_toepoch(2019, 9, 5, 11, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(50)
    rb.set_page(0)

    rb.add_column("Average of Experience Score",
                  "NLP_INSIGHT_POLARITY_SCORE", "AVG")

    rb.add_group_by("Category", "LTS_OC", "FIELD")
    rb.add_group_by("Location", "LOCATION_IDS", "FIELD")

    rb.add_filter("IN", "LOCATION_CUSTOM_PROPERTY", ["Hyatt"], {
                        "srcType": "CUSTOM",
                        "fieldName": "5ce45bf5e4b0a645c7d3e18a"
    })
    rb.add_filter("IN", "HIERARCHY_ID", ["5c484387e4b0e6a8e58d17b2"], {
                        "contentType": "DB_FILTER",
                        "ASSET_CLASS": "INTEL_LOCATION",
                        "withAssetLevel": True,
                        "withDimension": True
    })

    if rb.build_report_request():
        process_response(client.fetch_report(rb.request))
    else:
        print("Error building request:", rb.last_error)


def fetch_report_data_subject_categories():
    global client
    rb = sc.ReportBuilder()

    rb.set_engine("LISTENING")
    rb.set_name("SPRINKSIGHTS")

    rb.set_start_time(datetime_toepoch(2018, 9, 6, 0, 0))
    rb.set_end_time(datetime_toepoch(2019, 9, 15, 12, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(50)
    rb.set_page(0)

    rb.add_column("Avg. of Experience Score",
                  "NLP_INSIGHT_POLARITY_SCORE", "AVG")

    rb.add_group_by("LTS_NOC", "LTS_NOC", "FIELD")
    rb.add_group_by("Location IDs", "LOCATION_IDS", "FIELD")

    rb.add_filter("IN", "LOCATION_CUSTOM_PROPERTY", ["Hyatt"], {
                        "srcType": "CUSTOM",
                        "fieldName": "5ce45bf5e4b0a645c7d3e18a"
    })
    rb.add_filter("IN", "HIERARCHY_ID", ["5c484387e4b0e6a8e58d17b2"], {
                        "contentType": "DB_FILTER",
                        "ASSET_CLASS": "INTEL_LOCATION",
                        "withAssetLevel": True,
                        "withDimension": True
    })

    if rb.build_report_request():
        process_response(client.fetch_report(rb.request))
    else:
        print("Error building request:", rb.last_error)


def fetch_report_data_reviews():
    global client
    rb = sc.ReportBuilder()

    rb.set_engine("LISTENING")
    rb.set_name("SPRINKSIGHTS")

    rb.set_start_time(datetime_toepoch(2018, 9, 6, 0, 0))
    rb.set_end_time(datetime_toepoch(2019, 9, 15, 12, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(10)
    rb.set_page(0)

    rb.add_column("Avg. of Experience Score", "NLP_DOC_POLARITY_SCORE", "AVG")

    rb.add_group_by("Message", "ES_MESSAGE_ID", "FIELD")
    rb.add_group_by("Location IDs", "LOCATION_IDS", "FIELD", {"missing": 0})
    rb.add_group_by("Created Time", "SN_CREATED_TIME", "DATE_HISTOGRAM", {
        "interval": "1M"
    })
    rb.add_group_by("Star Rating", "STAR_RATING", "FIELD", {"missing": 0})

    rb.add_filter("IN", "HIERARCHY_ID", ["5c484387e4b0e6a8e58d17b2"], {
                        "contentType": "DB_FILTER",
                        "ASSET_CLASS": "INTEL_LOCATION",
                        "withAssetLevel": True,
                        "withDimension": True
    })

    if rb.build_report_request():
        print(json.dumps(rb.request, sort_keys=False, indent=4))
        process_response(client.fetch_report(rb.request))
    else:
        print("Error building request:", rb.last_error)


def fetch_report_metrics(report_engine, report_name):
    global client
    process_response(client.fetch_report_metrics_and_dimensions(
        report_engine, report_name))


def fetch_case_audit(flag):
    global client
    raw = (flag.upper() == "TRUE")
    rb = sc.ReportBuilder()
    rb.set_engine("PLATFORM")
    rb.set_name("CaseSLAReport")
    rb.set_start_time(datetime_toepoch(2019, 1, 1, 0, 0))
    rb.set_end_time(datetime_toepoch(2020, 2, 17, 12, 59))
    rb.set_time_zone("America/Denver")
    rb.set_page_size(100)
    rb.set_page(0)
    rb.add_group_by("Case ID", "CASE_ID", "FIELD")
    rb.add_filter("IN", "ARCHIVE", ["true"])

    audit_request = {
        "assetIds": [],
        "assetClass": "UNIVERSAL_CASE",
        "ascending": "false",
        "limit": 1000
    }
    if rb.build_report_request():
        if not raw:
            print("Report request:")
            print(rb.request)
        if client.fetch_report(rb.request):
            cases = client.result
            if "rows" in cases:
                if not raw:
                    print(json.dumps(cases, indent=4))
                    print("Cases Returned:", str(len(cases["rows"])))
                for case_id in cases["rows"]:
                    if client.fetch_case_by_case_id(case_id[0]):
                        case = client.result["data"]
                        audit_request["assetIds"].append(case["caseNumber"])
                        if not raw:
                            print("Case Id:", case_id[0], " - Case Number:", case["caseNumber"])
                if not raw:
                    print("Audit Request:", json.dumps(audit_request, indent=4))

                if client.fetch_audit(audit_request):
                    audit_records = client.result
                    if raw:
                        print(json.dumps(audit_records, indent=4))
                    else:
                        print("Number of change records returned:",str(len(audit_records["data"])))

                    for audit in audit_records["data"]:
                        if not raw:
                            print("Case:", audit["assetId"], " DateTime:", datetime_fromepoch(
                            audit["changeDate"]/1000), " Number of field changes:", str(len(audit["changes"])))
                else:
                    print("audit request failed", client.raw)
            else:
                print("No cases returned", client.raw)
        else:
            print("Error executing request", client.raw)
    else:
        print("Error building request:", rb.last_error)

def fetch_archived_cases():
    filter = {"query": "",
              "filters": [
                  {
                      "filterType": "IN",
                      "field": "channelType",
                      "values": ["SPRINKLR"]
                  },
                  {
                      "filterType": "IN",
                      "field": "archived",
                      "values": ["true"]
                  }
              ],
              "paginationInfo": {
                  "start": 0,
                  "rows": 100,
                  "sortKey":
                  "caseModificationTime"
              }}

    if client.search_case_v1(filter):
        cases = client.result
        print(json.dumps(cases))
        #for case in cases["searchResults"]:
        #    print(case['universalCaseApiDTO']['id'])
        #    # print(case["id"], " ", case["description"])
    else:
        print("Search Failed:", client.raw)


def fetch_webhook_types():
    global client
    process_response(client.fetch_webhook_types())


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
    workflow.assignment = case.Workflow.Assignment(
        "123", "USER", 123, now_as_epoch)
    workflow.modified_time = now_as_epoch
    workflow.campaign_id = 123  # campaign ID ?
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
    case.priority = "High"  # ?
    case.case_type = "Problem"
    case.external_case = case.External_Case(
        12345, "12345", "salesforce", None, now_as_epoch, now_as_epoch)
    case.contact = case.Contact(123, "Ariel Tritan")
    case.attachment = case_attachment
    case.due_date = now_as_epoch + 10000
    case.summary = "A new case created via API"
    case.created_time = now_as_epoch
    case.modified_time = now_as_epoch
    case.first_message_id = 123
    case.workflow = workflow

    client.create_case(case)


def fetch_case_by_number(case_number):
    global client
    process_response(client.fetch_case_by_number(case_number))


def fetch_message_by_id_and_source(message_id, source_type):
    global client
    process_response(client.fetch_message_by_id_and_source(
        message_id, source_type))


def fetch_message_by_umid(umid):
    global client
    process_response(client.fetch_message_by_UMID(umid))


def fetch_case_messages(case_id):
    global client
    process_response(client.fetch_case_associated_messages(case_id))


def fetch_user():
    global client
    process_response(client.fetch_user())


def fetch_user_by_id(user_id):
    global client
    process_response(client.fetch_user_by_id(user_id))

# def search_entity(entity_type, filter, sort, key, order='ASC')

def post_direct_message(twitter_handle):

        request={"messageType": 3,
            "accountId": 255156,
            "content": {
                "message": "If you're hAPI and you know it raise an exception!"
            },
            "taxonomy": {
                "campaignId": "033_124"
            }
        }


def date_time_toepoch(date_time):
    return datetime_toepoch(date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute)


def datetime_toepoch(year: int, month: int, day: int, hour=0, minute=0):
    return int(float(time.mktime(datetime.datetime(year, month, day, hour, minute).timetuple())) * 1000)


def datetime_fromepoch(epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S:{0:.0f}'.format(epoch%1000), time.localtime(epoch))


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
                # logging.debug("Result:" + str(client.result))
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
    print("SprinklrClientTest Authorize {apikey} {redirect_uri} [environment]")
    print("                   AssetSearch [One | Two | Three]")
    print("                   CreateCase")
    print(
        "                   FetchAccessToken {apikey} {secret} {code} {redirect uri}")
    print("                   FetchAccessibleUsers")
    print("                   FetchAccountCustomFields")
    print("                   FetchAllDashboards")
    print("                   FetchArchivedCases")
    print("                   FetchCaseByNumber {case_number}")
    print("                   FetchCaseMessagesById {case_id}")
    print("                   FetchCaseAudit {raw_flag}")
    print("                   FetchClients")
    print("                   FetchClientProfileLists")
    print("                   FetchClientUrlShortners")
    print("                   FetchClientQueues")
    print("                   FetchClientUsers")
    print("                   FetchDashboardByName {name}")
    print(
        "                   FetchDashboardStream {stream_id} {start} {rows} [{echo request} (True or False)]")
    print("                   FetchInboundCustomFields")
    print("                   FetchListeningTopics")
    print(
        "                   FetchListeningStream {id} {sinceTime} {untilTime}")
    print("                   FetchMacros")
    print("                   FetchMediaAssetCustomFields")
    print(
        "                   FetchMessageByIdAndSource {message_id} [ACCOUNT | PERSISTENT_SEARCH | LISTENING | BENCHMARKING | AUDIENCE | AUDIENCE_STUDY]}")
    print("                   FetchMessageByUMId {message_id}")
    print("                   FetchOutboundCustomFields")
    print("                   FetchPartnerAccountGroups")
    print("                   FetchPartnerAccounts")
    print("                   FetchPartnerCampaigns")
    print("                   FetchPartnerQueues")
    print("                   FetchPartnerUsers")
    print("                   FetchPermissions")
    print("                   FetchProfileCustomFields")
    print("                   FetchReport LOCATION | CATEGORIES | ATTRIBUTES | REVIEWS | AUDIT")
    print(
        "                   FetchReportMetrics {Report_Engine} {Report_Type}")
    print("                   FetchResources {resource type}")
    print("                   FetchUMPriorities")
    print("                   FetchUMStatuses")
    print("                   FetchUser")
    print("                   FetchUserById {User_Id}")
    print("                   FetchUserGroups")
    print("                   FetchWebhookTypes")
    print("                   RefreshAccessToken")


def main():
    global settings
    global client

    try:
        logging.basicConfig(filename='SprinklrClient.log', level=logging.DEBUG)
        logging.debug("Starting SprinklrClientTest with " +
                      str(len(sys.argv) - 1) + " actual parameters")

        settings = EasySettings("Sprinklr.conf")

        key = settings.get('key')
        path = settings.get('path')
        access_token = settings.get('access_token')

        if len(path) == 0:
            path = None

        # If using a differnent enviornment other that Prod, set path to that value (like 'prod2')
        client = sc.SprinklrClient(
            key=key, access_token=access_token, path=path)

        if len(sys.argv) > 1:
            command = str(sys.argv[1]).upper()

            if command == 'AUTHORIZE':
                if len(sys.argv) > 5:
                    print(
                        "Invalid command line - Usage: SprinklrClientTest Authorize {apikey} {redirect_uri} [environment]")
                else:
                    key = sys.argv[2]
                    redirect_uri = sys.argv[3]
                    if len(sys.argv) == 5:
                        path=sys.argv[4]
                    else:
                        path = None
                    client = sc.SprinklrClient(key)
                    authorize(key, redirect_uri, path)
            elif command == 'ASSETSEARCH':
                if len(sys.argv) != 3:
                    print(
                        "Invalid command line - Usage: SprinklrClientTest AssetSearch [One | Two | Three]")
                else:
                    if sys.argv[2].upper() == "ONE":
                        asset_search_one()
                    elif sys.argv[2].upper() == "TWO":
                        asset_search_two()
                    elif sys.argv[2].upper() == "THREE":
                        asset_search_three()
                    else:
                        print("Invalid Asset Search Option passed:",
                              sys.argv[2])
            elif command == "CREATECASE":
                create_case()
            elif command == 'FETCHALLDASHBOARDS':
                fetch_all_dashboards()
            elif command == 'FETCHACCESSTOKEN':
                if len(sys.argv) != 6:
                    print(
                        "Invalid command line - Usage: SprinklrClientTest GetAccessToken {path} {apikey} {secret} "
                        "{code} {redirect URI}")
                else:
                    path = sys.argv[2]
                    key = sys.argv[3]
                    secret = sys.argv[4]
                    code = sys.argv[5]
                    redirect = sys.argv[6]

                    client = sc.SprinklrClient(key, path)
                    success = client.fetch_access_token(
                        secret=secret, code=code, redirect_uri=redirect)

                    if success:
                        settings.set('access_token', client.access_token)
                        settings.set('refresh_token', client.refresh_token)
                        settings.set('redirect_uri', redirect)
                        settings.set('key', key)
                        settings.set('secret', secret)
                        settings.set('path', path),
                        settings.save()
                        print("Success")
                    else:
                        print(client.result)

                    key = settings.get('key')
                    access_token = settings.get('access_token')
                    client = sc.SprinklrClient(
                        key=key, access_token=access_token)
            elif command == 'FETCHACCESSIBLEUSERS':
                fetch_accessible_users()
            elif command == 'FETCHACCOUNTCUSTOMFIELDS':
                fetch_account_custom_fields()
            elif command == 'FETCHCASEAUDIT':
                fetch_case_audit(sys.argv[2])
            elif command == 'FETCHARCHIVEDCASES':
                fetch_archived_cases()
            elif command == "FETCHCASEBYNUMBER":
                fetch_case_by_number(sys.argv[2])
            elif command == "FETCHCASEMESSAGESBYID":
                fetch_case_messages(sys.argv[2])
            elif command == "FETCHCLIENTS":
                fetch_clients()
            elif command == 'FETCHCLIENTPROFILELISTS':
                fetch_client_profile_lists()
            elif command == "FETCHCLIENTURLSHORTNERS":
                fetch_client_url_shortners()
            elif command == 'FETCHCLIENTQUEUES':
                fetch_client_queues()
            elif command == 'FETCHCLIENTUSERS':
                fetch_client_users()
            elif command == 'FETCHDASHBOARDBYNAME':
                if len(sys.argv) != 3:
                    print(
                        "Invalid command line - Usage: SprinklrClientTest GetDashboardByName {name}")
                else:
                    fetch_dashboard_by_name(sys.argv[2])
            elif command == 'FETCHDASHBOARDSTREAM':
                fetch_dashboard_stream(sys.argv[2], sys.argv[3], sys.argv[4])
            elif command == 'FETCHINBOUNDCUSTOMFIELDS':
                fetch_inbound_custom_fields()
            elif command == 'FETCHLISTENINGTOPICS':
                fetch_listening_topics()
            elif command == 'FETCHLISTENINGSTREAM':
                if len(sys.argv) == 5:
                    fetch_listening_stream(
                        sys.argv[2], sys.argv[3], sys.argv[4])
                elif len(sys.argv) == 6:
                    fetch_listening_stream(
                        sys.argv[2], sys.argv[3], sys.argv[4], echo_request=sys.argv[5])
            elif command == 'FETCHMACROS':
                fetch_macros()
            elif command == 'FETCHMEDIAASSETCUSTOMFIELDS':
                fetch_media_asset_custom_fields()
            elif command == 'FETCHMESSAGEBYIDANDSOURCE':
                fetch_message_by_id_and_source(sys.argv[2], sys.argv[3])
            elif command == 'FETCHMESSAGEBYUMID':
                fetch_message_by_umid(sys.argv[2])
            elif command == 'FETCHOUTBOUNDCUSTOMFIELDS':
                fetch_outbound_custom_fields()
            elif command == 'FETCHPARTNERACCOUNTGROUPS':
                fetch_partner_account_groups()
            elif command == 'FETCHPARTNERACCOUNTS':
                fetch_partner_accounts()
            elif command == 'FETCHPARTNERCAMPAIGNS':
                fetch_partner_campaigns()
            elif command == 'FETCHPARTNERQUEUES':
                fetch_partner_queues()
            elif command == 'FETCHPARTNERUSERS':
                fetch_partner_users()
            elif command == 'FETCHPERMISSIONS':
                fetch_permissions()
            elif command == 'FETCHPROFILECUSTOMFIELDS':
                fetch_profile_custom_fields()
            elif command == "FETCHREPORT":
                if sys.argv[2].upper() == "LOCATION":
                    fetch_report_data_location_analyisis()
                elif sys.argv[2].upper() == "CATEGORIES":
                    fetch_report_data_subject_categories()
                elif sys.argv[2].upper() == "ATTRIBUTES":
                    fetch_report_data_attibutes()
                elif sys.argv[2].upper() == "REVIEWS":
                    fetch_report_data_reviews()
                elif sys.argv[2].upper() == "AUDIT":
                    fetch_report_user_audit()
                else:
                    print("Report not found")
            elif command == "FETCHREPORTMETRICS":
                fetch_report_metrics(sys.argv[2], sys.argv[3])
            elif command == 'FETCHRESOURCES':
                fetch_resources(sys.argv[2])
            elif command == 'FETCHUSER':
                fetch_user()
            elif command == 'FETCHUSERBYID':
                fetch_user_by_id(sys.argv[2])
            elif command == 'FETCHUMPRIORITIES':
                fetch_um_priorities()
            elif command == 'FETCHUMSTATUSES':
                fetch_um_statuses()
            elif command == "FETCHUSERGROUPS":
                fetch_user_groups()
            elif command == "FETCHWEBHOOKTYPES":
                fetch_webhook_types()
            elif command == "REFRESHACCESSTOKEN":
                key = settings.get('key')
                secret = settings.get('secret')
                redirect = settings.get('redirect_uri')
                refresh_access_token = settings.get('refresh_token')

                client = sc.SprinklrClient(key)

                success = client.refresh_access_token(
                    key, secret, redirect, refresh_access_token)

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
