import SprinklrClient as sc
import json
from easysettings import EasySettings
import sys
from datetime import timezone
import datetime
import time

# from datetime import datetime
# import logging

client = None
settings = None

def get_access_token(code):
    global client
    secret = settings.get('secret')
    redirect = settings.get('redirect')

    print("Secret = ", secret)
    print("redirect = ", redirect)
    print("code = ", code)
    print("key =", client)
    success = client.get_access_token(secret=secret, redirect_uri=redirect, code=code)

    if success:
        print("Encoding:", client.encoding)
        print("Last Status Code:", client.last_status_code)
        print("Access Token:", client.access_token)
        print("Refresh Token:", client.refresh_token)

    else:
        if client.status_message is not None:
            j_result = json.loads(client.status_message)
            print("Error: ", json.dumps(j_result, indent=4, sort_keys=True))


def get_all_dashboards():
    global client
    success = client.request_all_dashboards()
    if success:
        print(json.dumps(client.result, sort_keys=True, indent=4))
    else:
        print(client.status_message)


def get_dashboard_by_name(dashboard_name):
    global client

    success = client.request_dashboard_by_name(dashboard_name)

    if success:
        dashboard = client.result
        print(json.dumps(dashboard, sort_keys=True, indent=4))
    else:
        print(client.status_message)


def get_dashboard_stream(dashboard_id, start, rows):
    global client

    success = client.request_dashboard_stream(dashboard_id=dashboard_id, start=start, rows=rows)

    if success:
        dashboard = client.result
        print(json.dumps(dashboard, sort_keys=True, indent=4))
    else:
        print(client.status_message)


def get_listening_topics():
    global client

    success = client.get_listening_topics()
    if success:
        print(json.dumps(client.result, sort_keys=True, indent=4))
    else:
        print(client.status_message)


def get_listening_stream(filter_value, since_time, until_time, timezone_offset=14400000, time_field="SN_CREATED_TIME",
                         details="STREAM", dimension="TOPIC", metric="MENTIONS", trend_aggregation_period=None, start=1,
                         rows=100, echo_request=False, tag=None, sort_key=None, message_format_options=None):
    global client

    success = client.get_listening_stream(filter_value, since_time, until_time, timezone_offset, time_field,
                                          details, dimension, metric, trend_aggregation_period, start,
                                          rows, echo_request, tag, sort_key, message_format_options)

    if success:
        print(json.dumps(client.result, sort_keys=True, indent=4))
    else:
        print(client.status_message)


def get_resources(types):
    global client
    success = client.get_resources(types)

    if success:
        print(json.dumps(client.result, sort_keys=True, indent=4))
    else:
        print(client.status_message)


def datetime_toepoch(year, month, day, hour=0, minute=0):
    return int(float(time.mktime(datetime.datetime(year, month, day, hour,minute).timetuple())) * 1000)

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

    if rb.build_request():
        success = client.report_query(rb.request)
        if success:
            print(json.dumps(client.result, sort_keys=False, indent=4))
        else:
            print(client.status_message)

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

    if rb.build_request():
        success = client.report_query(rb.request)
        if success:
            print(json.dumps(client.result, sort_keys=False, indent=4))
        else:
            print(client.status_message)

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

    if rb.build_request():
        success = client.report_query(rb.request)
        if success:
            print(json.dumps(client.result, sort_keys=False, indent=4))
        else:
            print(client.status_message)

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

    if rb.build_request():
        success = client.report_query(rb.request)
        if success:
            print(json.dumps(client.result, sort_keys=False, indent=4))
        else:
            print(client.status_message)

    else:
        print("Error building request:", rb.last_error)


def get_report_metrics(report_engine, report_name):
    global client
    success = client.get_report_metrics(report_engine, report_name)

    if success:
        print(json.dumps(client.result, sort_keys=True, indent=4))
    else:
        print(client.status_message)

def get_webhook_types():
    global client

    success = client.get_webhook_types()
    if success:
        print(json.dumps(client.result, sort_keys=True, indent=4))
    else:
        print(client.status_message)    

def main():
    global settings
    global client

    settings = EasySettings("Sprinklr.conf")

    if len(sys.argv) > 1:
        command = str(sys.argv[1]).upper()

        if command == 'GETACCESSTOKEN':
            if len(sys.argv) != 6:
                print(
                    "Invalid command line - Usage: SprinklrClientTest GetAccessToken {apikey} {secret} "
                    "{code} {redirect URI}")
            else:
                key = sys.argv[2]
                secret = sys.argv[3]
                code = sys.argv[4]
                redirect = sys.argv[5]

                client = sc.Sprinklr(key)

                success = client.get_access_token(secret=secret, code=code, redirect_uri=redirect)

                if success:
                    settings.set('access_token', client.access_token)
                    settings.set('refresh_token', client.refresh_token)
                    settings.set('key', key)
                    settings.save()
                else:
                    print(client.status_message)
        else:
            key = settings.get('key')
            access_token = settings.get('access_token')
            client = sc.Sprinklr(key=key, access_token=access_token)

            if command == 'GETALLDASHBOARDS':
                get_all_dashboards()

            elif command == 'GETDASHBOARDBYNAME':
                if len(sys.argv) != 3:
                    print("Invalid command line - Usage: SprinklrClientTest GetDashboardByName {name}")

                get_dashboard_by_name(sys.argv[2])

            elif command == 'GETDASHBOARDSTREAM':
                get_dashboard_stream(sys.argv[2], sys.argv[3], sys.argv[4])
            elif command == 'GETLISTENINGTOPICS':
                get_listening_topics()
            elif command == 'GETLISTENINGSTREAM':
                if len(sys.argv) == 5:
                    get_listening_stream(sys.argv[2], sys.argv[3], sys.argv[4])
                elif len(sys.argv) == 6:
                    get_listening_stream(sys.argv[2], sys.argv[3], sys.argv[4], echo_request=sys.argv[5])
            elif command == 'GETRESOURCES':
                get_resources(sys.argv[2])
            elif command == "GETREPORT":
                if sys.argv[2].upper() == "LOCATION":
                    get_report_data_location_analyisis()
                elif sys.argv[2].upper() == "CATEGORIES":
                    get_report_data_subject_categories()
                elif sys.argv[2].upper() == "ATTRIBUTES":
                    get_report_data_attibutes() 
                elif sys.argv[2].upper() == "REVIEWS":
                    get_report_data_reviews() 
            elif command == "GETREPORTMETRICS":
                get_report_metrics(sys.argv[2], sys.argv[3])
            elif command == "GETWEBHOOKTYPES":
                get_webhook_types()
            
    else:
        print("Usage:")
        print("SprinklrClientTest GetAccessToken {apikey} {secret} {code} {redirect uri}")
        print("                   GetAllDashboards")
        print("                   GetDashboardByName {name}")
        print("                   GetDashboardStream {stream_id} {start} {rows} [{echo request} (True or False)]")
        print("                   GetListeningTopics")
        print("                   GetResources {resource type}")
        print("                   GetListeningStream {id} {sinceTime} {untilTime}")
        print("                   GetReport LOCATION | CATEGORIES | ATTRIBUTES | REVIEWS")
        print("                   GetReportMetrics {Report_Engine} {Report_Type}")
        print("                   GetWebhookTypes")

if __name__ == "__main__":
    main()
