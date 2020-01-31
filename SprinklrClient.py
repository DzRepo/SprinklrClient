import requests
import json
import urllib.parse
import logging
from SprinklrCase import CaseCreate, CaseUpdate
from SprinklrReport import ReportBuilder

HTTP_OK = 200

class SprinklrClient:
    """Sprinklr Client Library"""

    def __init__(self, key, path=None, access_token=None):
        self.last_status_code = HTTP_OK
        self.encoding = None
        self.access_token = access_token
        self.refresh_token = None
        self.token_type = None
        self.expires_in = None
        self.status_code = None
        self.status_message = None
        self.result = None
        self.key = key
        self.raw = None
        self.search_cursor = None

        # current valid path options are (None), prod0, prod2, or sandbox
        if path is not None:
            if path.endswith("/"):
                self.path = path
            else:
                self.path = path + "/"
        else:
            self.path = ""
        logging.info("Client initialized. Path is |" + self.path + "|")
        
# HTTP Methods
    def delete_request(self, request_url: str, data = None):
        """
        :rtype: object
        """

        response = None

        headers = {'key': self.key,
                   'Authorization': "Bearer " + self.access_token,
                   'Content-Type': 'application/json',
                   'cache-control': 'no-cache'}

        logging.info("Posting to URL:" + request_url)

        try:
            response = requests.delete(url=request_url, headers=headers, data=json.dumps(data))
        except ConnectionError:
            logging.error("Connection Error:" + request_url)
            self.status_message = "Connection Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except TimeoutError:
            logging.error("Timeout Error:" + request_url)
            self.status_message = "Timeout Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except requests.exceptions.RequestException:
            logging.error("Reqeust Error:" + request_url)
            self.status_message = "Request Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)

        if response is not None:
            self.status_code = response.status_code
            self.raw = response.text
            self.result = json.loads(response.text)

        if self.status_code != HTTP_OK:
            logging.error('delete_request:' + response.text)

        return self.status_code == HTTP_OK

    def get_request(self, request_url, returns_json=False):
        headers = {'key': self.key,
                   'Authorization': "Bearer " + self.access_token}

        if returns_json:
            headers['accept'] = 'application/json'

        response = None

        logging.debug("Requesting URL:" + request_url)
        try:
            response = requests.get(url=request_url, headers=headers)
            logging.debug("response code:" + str(response.status_code))
        except ConnectionError:
            logging.error("Connection Error:" + request_url)
            self.status_message = "Connection Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except TimeoutError:
            logging.error("Timeout Error:" + request_url)
            self.status_message = "Timeout Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except requests.exceptions.RequestException:
            logging.error("Reqeust Error:" + request_url)
            self.status_message = "Request Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)

        if response is not None:
            self.status_code = response.status_code
            self.raw = response.text
            try:
                self.result = json.loads(response.text)
            except Exception:
                self.result = response.text

        if self.status_code != HTTP_OK:
            logging.error('get_request:' + response.text)
            self.status_message = response.text

        return self.status_code == HTTP_OK

    def post_request(self, request_url: str, data: object):
        """

        :rtype: object
        """

        response = None

        headers = {'key': self.key,
                   'Authorization': "Bearer " + self.access_token,
                   'Content-Type': 'application/json',
                   'cache-control': 'no-cache'}

        logging.info("Posting to URL:" + request_url)
        logging.debug("Data Being Posted:" + str(data))

        try:
            response = requests.post(url=request_url, headers=headers, data=json.dumps(data))
        except ConnectionError:
            logging.error("Connection Error:" + request_url)
            self.status_message = "Connection Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except TimeoutError:
            logging.error("Timeout Error:" + request_url)
            self.status_message = "Timeout Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except requests.exceptions.RequestException:
            logging.error("Reqeust Error:" + request_url)
            self.status_message = "Request Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)

        if response is not None:
            self.status_code = response.status_code
            self.raw = response.text
            self.result = json.loads(response.text)

        if self.status_code != HTTP_OK:
            logging.error('post_request:' + response.text)

        return self.status_code == HTTP_OK

    def put_request(self, request_url: str, data = None):
        """
        :rtype: object
        """

        response = None

        headers = {'key': self.key,
                   'Authorization': "Bearer " + self.access_token,
                   'Content-Type': 'application/json',
                   'cache-control': 'no-cache'}

        logging.info("Posting to URL:" + request_url)

        try:
            response = requests.put(url=request_url, headers=headers, data=json.dumps(data))
        except ConnectionError:
            logging.error("Connection Error:" + request_url)
            self.status_message = "Connection Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except TimeoutError:
            logging.error("Timeout Error:" + request_url)
            self.status_message = "Timeout Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except requests.exceptions.RequestException:
            logging.error("Reqeust Error:" + request_url)
            self.status_message = "Request Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)

        if response is not None:
            self.status_code = response.status_code
            self.raw = response.text
            self.result = json.loads(response.text)

        if self.status_code != HTTP_OK:
            logging.error('put_request:' + response.text)

        return self.status_code == HTTP_OK

#Account
    def get_account_by_channel_id(self, accountType, channelId):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/account/{accountType}/{channelId}'
        return self.get_request(request_url, returns_json=True)

    def delete_account(self, accountId):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/account/{accountId}'
        return self.delete_request(request_url)

    def update_custom_properties(self, accountId, properties):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/account/update/{accountId}/customProperties'
        return self.put_request(request_url, data=properties)

    def update_account_visibility(self, accountId, permissions):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/account/{accountId}/visibility-permissions'
        return self.put_request(request_url, permissions)

# Authorize
    # this endpoint only returns the URL used to start the authorization process. It does not invoke the web-browser required workflow.
    def authorize(self, api_key, redirect_uri):
        request_url = f'https://api2.sprinklr.com/{self.path}oauth/authorize?client_id={api_key}&response_type=code&redirect_uri={redirect_uri}'
        return request_url

    # using the secret key and 'code' returned from the authoize process, retrieve the access and refresh tokens        
    def get_access_token(self, secret="", redirect_uri='', code=""):
            """
                    Get Access Token based on code returned via authorization process
                    :return: Dictionary of Dashboard columns
                    """
            logging.info("Calling get_access_token")
            request_url = (f'https://api2.sprinklr.com/{self.path}oauth/token?'
                        f'client_id={self.key}&'
                        f'client_secret={secret}&'
                        f'redirect_uri={redirect_uri}&'
                        f'grant_type=authorization_code&'
                        f'code={code}')

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(url=request_url, headers=headers)

            self.raw = response

            self.status_code = response.status_code

            if response.status_code == HTTP_OK:
                self.encoding = response.encoding
                j_result = json.loads(response.content)
                self.access_token = j_result["access_token"]
                self.token_type = j_result["token_type"]
                self.refresh_token = j_result["refresh_token"]
            else:
                logging.error("get_access_code - url:" + request_url)
                if response.content is not None:
                    self.result = response.content

            return response.status_code == HTTP_OK

    def refresh_access_token(self, api_key, secret, redirect_uri, refresh_token):
        logging.info("Calling refresh_access_token")
        request_url = f'https://api2.sprinklr.com/{self.path}oauth/token?client_id={api_key}&client_secret={secret}&redirect_uri={redirect_uri}&grant_type=refresh_token&refresh_token={refresh_token}'
        headers = {'Content-Type': 'Application/x-www-form-urlencoded'}
        response = requests.post(url=request_url, headers=headers)
        
        self.status_code = response.status_code

        if response.status_code == HTTP_OK:
            self.encoding = response.encoding
            j_result = json.loads(response.content)
            self.access_token = j_result["access_token"]
            self.token_type = j_result["token_type"]
            self.refresh_token = j_result["refresh_token"]
        else:
            if response.content is not None:
                self.result = response.content
        return response.status_code == HTTP_OK

# Assets 1.0
    
    def asset_create(self, asset_data):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam'
        return self.post_request(request_url, data=asset_data)   

    def asset_delete(self, asset_id):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/{asset_id}'
        return self.delete_request(request_url, None)
    
    def asset_import(self, import_type, url, upload_tracker_id):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/importUrl?importType={import_type}&url={url}&uploadTrackerId={upload_tracker_id}'
        return self.post_request(request_url, None)

    def asset_read(self, asset_id):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/{asset_id}'
        return self.get_request(request_url, returns_json=True)

    def asset_search(self, filters, sort_list, keyword_search, range_condition, only_available=False, start=0, rows=20):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/search'
        request = {
            "filters":filters,
            "sortList":sort_list,
            "keywordSearch":keyword_search,
            "rangeCondition":keyword_search,
            "onlyAvailable":only_available,
            "start":start,
            "rows":rows
        }
        return requests.post(request_url, data=request)
   
    def asset_update(self, asset_id, name, description, asset_status, expiry_time, available_after_time, 
                     tags, share_config, campaign_id, partner_custom_fields, client_custom_properties, restricted=None):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/{asset_id}'
        data = {}
        return self.put_request(request_url, data)
    
    # TODO: File upload - may nead to alter post to or pull in single instance version    
    def asset_upload(self, content_type, upload_tracker_id, file_name):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/upload?contentType={content_type}&uploadTrackerId={upload_tracker_id}'
        data = {}
        return self.post_request(request_url, data)

# Assets 2.0

    def create_asset_group(self, asset_group):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/asset-group'
        return self.post_request(request_url, data=asset_group)

    def get_asset_group(self, groupId):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/asset-group/{groupId}'
        return self.get_request(request_url)

    def update_asset_group(self, groupId, asset_update):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/asset-group/{groupId}'
        return self.put_request(request_url, data=asset_update)

    def delete_asset_group(self, groupId):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/asset-group/{groupId}'
        return self.delete_request(request_url)

# Audit

    def get_audit(self):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/audit/fetch'
        return self.get_request(request_url)

# Bootstrap
    def get_partner_campaigns(self):
        return self.get_resources('PARTNER_CAMPAIGNS')

    def get_webhook_types(self):
        request_url = f"https://api2.sprinklr.com/{self.path}api/v2/webhook-subscriptions/webhook-types"
        
        self.get_request(request_url)
        return self.status_code == HTTP_OK
  
    def get_resources(self, types):

        request_url = f"https://api2.sprinklr.com/{self.path}api/v1/bootstrap/resources?types={types}"

        self.get_request(request_url)
        return self.status_code == HTTP_OK

    def get_macros(self):
        return self.get_resources('MACROS')

    def get_client_profile_lists(self):
        return self.get_resources('CLIENT_PROFILE_LISTS')

    def get_partner_profile_lists(self):
        return self.get_resources('PARTNER_PROFILE_LISTS')

    def get_client_queues(self):
        return self.get_resources('CLIENT_QUEUES')

    def get_partner_queues(self):
        return self.get_resources('PARTNER_QUEUES')

    def get_approval_paths(self):
        return self.get_resources('APPROVAL_PATHS')

    def get_accessible_users(self):
        return self.get_resources('ACCESSIBLE_USERS')

    def get_um_priorities(self):
        return self.get_resources('UM_PRIORITIES')

    def get_um_statuses(self):
        return self.get_resources('UM_STATUSES')

    def get_partner_accounts(self):
        return self.get_resources('PARTNER_ACCOUNTS')

# Campaigns 1.0

    def create_campaign(self, campaign_data):
        request_url = f'https://api2.sprinklr.com/{self.path}/api/v1/campaign'
        return self.post_request(request_url, campaign_data)

# Campaigns 2.0

# Case 1.0

    def create_case_v1(self, case_data):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/case'
        return self.post_request(request_url, data=case_data)

    def delete_case_v1(self, case_id):
        request_url = f'https://api2.sprinklr.com/{{env}}/api/v1/case'
        return self.delete_request(request_url, )

    def search_case_v1(self, search_parameters):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/case/search'
        return self.post_request(request_url, data=search_parameters)

    def update_case_v1(self, update_parameters):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/case/update'
        return self.post_request(request_url, data=update_parameters)

# Case 2.0

    def create_case_v2(self, case: CaseCreate):
    
            request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case'

            case.build_create_request()

            #print(case.request)           
            print(json.dumps(case.request))

            '''
            response = self.post_request(request_url, request)

            self.status_code = response.status_code

            if response.status_code == HTTP_OK:
                self.encoding = response.encoding
                j_result = json.loads(response.content)
                self.result = j_result
            else:
                if response.content is not None:
                    self.result = response.content

            return response.status_code == HTTP_OK
            '''

    def get_case_by_number(self, case_number):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/case-numbers?case-number={case_number}'
        return self.get_request(request_url, returns_json=True)

    def get_case_by_channel_case_id(self, channel_case_id):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/channel-case-ids?channelCaseIds={channel_case_id}'
        return self.get_request(request_url, returns_json=True)

    def get_case_by_channel_case_number(self, chanel_case_number):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/channel-case-numbers?channelCaseNumbers={chanel_case_number}'
        return self.get_request(request_url, returns_json=True)
    
    def get_case_by_case_id(self, case_id):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/{case_id}'
        return self.get_request(request_url, returns_json=True)

    def get_case_associated_messages(self, case_id):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/associated-messages?id={case_id}'
        return self.get_request(request_url, returns_json=True)

    def delete_case_v2(self, case_id):
        delete_url = f'https://api2.sprinklr.com/{self.path}api/v2/case'
    
        data = { case_id }
        return self.delete_request(delete_url, data)

    def update_case_v2(self, case_id : int, case : CaseUpdate):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case'
        
        
        response = self.put_request(request_url, case)

        self.status_code = response.status_code

        if response.status_code == HTTP_OK:
            self.encoding = response.encoding
            j_result = json.loads(response.content)
            self.result = j_result
        else:
            if response.content is not None:
                self.result = response.content

        return response.status_code == HTTP_OK

# Comment
    def search_comments(self, asset_id, asset_class):
        request_url=f'https://api2.sprinklr.com/{self.path}api/v1/generic/comment/search/{asset_class}/{asset_id}'
        return self.post_request(request_url, data=None)

# Short URL
 
    def get_client_url_shortners(self):
        return self.get_resources('CLIENT_URL_SHORTNERS')

    def create_short_url(self, shortner_id, link):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/link/shorten'
        post_data = {
            "link": {link},
            "urlShortnerId": {shortner_id}
        }
        return self.post_request(request_url, data=post_data)

# Custom Fields
    def create_custom_field(self, post_data):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/customfield'
        self.post_request(request_url, data=post_data)

    def search_custom_field(self, search_data):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/customfield/search'
        self.post_request(request_url, data=search_data)

# TODO ------------- CUSTOM FIELD UPDATE is next

    def get_profile_custom_fields(self):
        return self.get_resources('PROFILE_CUSTOM_FIELDS')

    def get_account_custom_fields(self):
        return self.get_resources('ACCOUNT_CUSTOM_FIELDS')

    def get_media_asset_custom_fields(self):
        return self.get_resources('MEDIA_ASSET_CUSTOM_FIELDS')

    def get_outbound_custom_fields(self):
        return self.get_resources('OUTBOUND_CUSTOM_FIELDS')

    def get_inbound_custom_fields(self):
        return self.get_resources('INBOUND_CUSTOM_FIELDS')

# Engagement Dashboard
    def request_all_dashboards(self):
        """
        request all dashboards
        :return: Dictionary of Engagement Dashboard
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/dashboards'
        return self.get_request(request_url)
        
    def request_dashboard_by_name(self, dashboard_name: str):
        """
        request dashboard data by name
        :return: dashboard metadata and column descriptions
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/dashboard/{urllib.parse.quote(dashboard_name)}'

        self.get_request(request_url)
        return self.status_code == HTTP_OK

    def request_dashboard_stream(self, dashboard_id, start=0, rows=21,
                                 since_date=None, until_date=None, sort='snCreatedTime%20desc'):
        """
        request dashboard data by name
        :return: dashboard contents
        """

        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/stream/{dashboard_id}' \
            f'/feed?sort={sort}&rows={rows}&meta=true&start={start}'

        if since_date is not None:
            request_url += "&sinceDate=" + since_date

        if until_date is not None:
            request_url += "&untilDate=" + until_date

        self.get_request(request_url)
        return self.status_code == HTTP_OK

# Extensions

# Listening
    def get_listening_insight_volume_trend(self, since_time, until_time, metric="MENTIONS", timezone_offset=0, dimension=None, filter_value=None):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/listening/query/widget'

        request_data = \
            {"sinceTime": since_time,
             "untilTime": until_time,
             "timezoneOffset": timezone_offset,
             "details": {
                 "widgetType": "TREND"
             },
             "filters": [
                 {"dimension": dimension,
                  "filterValues": [filter_value]}
             ],
             "metric": metric,
             }
        self.post_request(request_url, request_data)
        return self.status_code == HTTP_OK

    def get_listening_topics(self):
        """
        request all listening topics
        :return: Dictionary of listening topics
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/listening/topics'

        logging.info("Calling get_listening_topics")

        self.get_request(request_url)
        return self.status_code == HTTP_OK

    def get_listening_stream(self, filter_value, since_time, until_time, timezone_offset=14400000,
                             time_field="SN_CREATED_TIME", details="STREAM", dimension="TOPIC",
                             metric="MENTIONS", trend_aggregation_period=None, start=1, rows=100,
                             echo_request=False, tag=None, sort_key=None, message_format_options=None):

        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/listening/query/stream'
        # Sample Request Data
        # '{
        #     "sinceTime": "1544418000000",
        #     "untilTime": "1547152918520",
        #     "details": {
        #         "widgetType": "STREAM"
        #     },
        #     "filters": [
        #         {
        #             "dimension": "TOPIC",
        #             "filterValues": [
        #                 "595c50dbe4b064e21f85d074"
        #             ]
        #         }
        #     ],
        #     "metric": "MENTIONS",
        #     "timezoneOffset": 14400000,
        #     "rows": 100,
        #     "start": 1
        # }'
        #

        request_data = \
            {"sinceTime": since_time,
             "untilTime": until_time,
             "timeField": time_field,
             "timezoneOffset": timezone_offset,
             "details": {"widgetType": details},
             "filters": [
                 {"dimension": dimension,
                  "filterValues": [filter_value]}
             ],
             "metric": metric, "start": start, "rows": rows,
             }

        # The trend aggregate period; applicable for TREND and GROUPED_TREND Widget
        # {HOUR, DAY, WEEK, MONTH, QUARTER, YEAR}
        if trend_aggregation_period is not None:
            request_data["trendAggregationPeriod"] = trend_aggregation_period

        # A text value that is sent and returned unaltered, so topics can be stored and associated correctly.
        if tag is not None:
            request_data["tag"] = tag

        # sortKey can take one of 3 values:
        # ‘SYSTEM_CREATED_TIME’ - system created time
        # ‘CREATED_TIME’ - social network created time (default)
        # ‘MODIFIED_TIME’ - modified time
        # It sorts the response messages based upon the specified field.
        if sort_key is not None:
            request_data["sortKey"] = sort_key

        if echo_request is not None:
            request_data["echoRequest"] = echo_request

        # Comma delimit format values = {strip_html, text strip_url, include_original}
        # strip_html - Strip html from the message text
        # strip_url - Strip Urls from the message text
        # include_original - Include the original text as well in the field "originalText"
        if message_format_options is not None:
            request_data["messageFormatOptions"] = message_format_options

        self.post_request(request_url, data=request_data)

        return self.status_code == HTTP_OK

# Message 1.0

# Message 2.0
    def get_message_by_id_and_source(self, message_id, source_type):
       request_url = f'https://api2.sprinklr.com/{self.path}api/v2/message?id={message_id}&sourceType={source_type}'
       return self.get_request(request_url, returns_json=True)
       
    def report_query(self, data):
        request_url = f' https://api2.sprinklr.com/{self.path}api/v1/reports/query'
    
        self.post_request(request_url, data)
        return self.status_code == HTTP_OK
    
    def get_report_metrics(self, report_engine, report_type):
        request_url = f"https://api2.sprinklr.com/{self.path}api/v1/reports/metadata/{report_engine}?{report_type}"

        self.get_request(request_url)
        return self.status_code == HTTP_OK

# Reporting 2.0

# SAM

# Search

    class Filter:
        def __init__(self):
                self.type = None
                self.filters = []

    class Filters:
        def __init__(self):
                self.type = None
                self.key = None
                self.values = []

    def search_entity(self, entity_type, filter : Filter, sort_order = 'ASC', sort_key='id', page_size = 0):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/search/{entity_type}'

        request_data = \
            {"filter": filter,
             "sort": {
                 "key": sort_key,
                 "order": sort_order
             },
             "page": {
                 'size': page_size
                }
             }
        if (self.post_request(request_url, request_data)):
            self.search_cursor = self.result["data"]["cursor"]
        else:
             self.search_cursor = None

    def search_campaign(self, filter,  sort_order = 'ASC', sort_key='name', page_size = 20):
        return self.search_entity('CAMPAIGN', filter, sort_order, sort_key, page_size)

    def search_campaign_next(self):
        return self.search_next_page("CAMPAIGN")
        
    def search_case(self, filter,  sort_order = 'ASC', sort_key='id', page_size = 20):
        return self.search_entity('CASE', filter, sort_order, sort_key, page_size)

    def search_case_next(self):
        return self.search_next_page("CASE")

    def search_message(self, filter, sort_order = 'ASC', sort_key='id', page_size = 20):
        return self.search_entity('MESSAGE', filter, sort_order, sort_key, page_size)

    def search_message_next(self):
        return self.search_next_page("MESSAGE")

    def search_sam(self, filter, sort_order = 'ASC', sort_key='name', page_size = 20):
        return self.search_entity('SAM', filter, sort_order, sort_key, page_size)

    def search_sam_next(self):
        return self.search_next_page("SAM")

    def search_next_page(self, entity_type):
        if self.search_cursor is not None:
            request_url = f'https://api2.sprinklr.com/{self.path}api/v2/search/{entity_type}?id={self.search_cursor}'
            return self.get_request(request_url)
        else:
            return False
  
# Users
    def get_user(self):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/me'
        
        self.get_request(request_url)
        return self.status_code == HTTP_OK

    def get_user_by_id(self, user_id):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/scim/v2/Users/{user_id}'
        
        self.get_request(request_url)
        return self.status_code == HTTP_OK

    def get_user_groups(self):
        return self.get_resources('USER_GROUPS')

    def get_permissions(self):
        return self.get_resources('PERMISSIONS')

    def get_clients(self):
        return self.get_resources('CLIENTS')

    def get_client_users(self):
        return self.get_resources('CLIENT_USERS')

    def get_partner_users(self):
        return self.get_resources('PARTNER_USERS')

    def get_partner_account_groups(self):
        return self.get_resources('PARTNER_ACCOUNT_GROUPS')

# Paid Initiative

# Product

# Profile 1.0

# Profile 2.0

# Publishing 1.0

# Publishing 2.0

# Reporting 1.0

# Streams
