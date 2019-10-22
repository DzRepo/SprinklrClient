import requests
import json
import urllib.parse
import logging

HTTP_OK = 200


class ReportBuilder:
    def __init__(self):
        self.engine = None
        self.name = None
        self.page = 0
        self.start_time = None  # Unix time in ms
        self.end_time = None    # Unix time in ms
        self.time_zone = None   # UTC is default
        self.page_size = 10     # Rows to be returned per call - default is 10, max is 2000
        self.page = 0           # page to request - default is 0 (first)
        self.projections = []
        self.group_bys = []
        self.group_by_projections = []
        self.group_by_sorts = []
        self.group_by_filters = []
        self.columns = []
        self.request = None
        self.filters = []
        self.projection_decorations = []
        self.last_error = None

    def set_engine(self, engine_name):
        if engine_name.upper() in {"AD", "PLATFORM", "INBOUND_MESSAGE", "LISTENING"}:
            self.engine = engine_name.upper()
            return True
        else:
            return False

    def set_name(self, name):
        self.name = name
        return True

    def set_page(self, page):
        if page > 0:
            self.page = page
            return True
        else:
            self.page = 0
            return False

    def set_start_time(self, start_time):
        self.start_time = start_time
        return True

    def set_end_time(self, end_time):
        self.end_time = end_time
        return True

    def set_time_zone(self, time_zone):
        self.time_zone = time_zone
        return True

    def set_page_size(self, page_size):
        self.page_size = page_size
        return True

    # {"heading": "HIERARCHY_PATH", "dimensionName": "HIERARCHY_PATH", "groupType": "FIELD", "details": {}
    # Valid group_types: DATE_HISTOGRAM, TIME_OF_DAY, DAY_OF_WEEK, MONTH_OF_YEAR, FIELD

    def add_group_by(self, heading, dimension_name, group_type, details=None):
        self.group_bys.append({
            "heading": heading,
            "dimensionName": dimension_name,
            "groupType": group_type,
            "details": details,
            })


    # {"filterType": "IN", "dimensionName": "HIERARCHY_ID", "values": ["5c3db128e4b0dcecf6fa1c73"], "details": {}}
    # based on report_engine, different filter_types are valid.
    # for PLATFORM and INBOUND_MESSAGE, the following are valid:
    #    IN, GT, GTE, LT, LTE, NIN, BETWEEN, STARTS_WITH, CONTAINS, EQUALS , FILTER, EXISTS
    def add_filter(self, filter_type, dimension_name, values, details=None):
        self.filters.append({
            "filterType": filter_type,
            "dimensionName": dimension_name,
            "values": values,
            "details": details
        })

    # {"heading": "MENTIONS_COUNT", "measurementName": "MENTIONS_COUNT", "aggregateFunction": "SUM" }
    # Valid aggregate_function parameters: SUM, AVG, MIN, MAX, STATS
    def add_column(self, heading, measurement_name, aggregate_function, details=None):
        self.columns.append({
            "heading": heading,
            "measurementName": measurement_name,
            "aggregateFunction": aggregate_function,
            "details": details
        })
    
    def build_request(self):
        try:
            self.request = {
                "reportingEngine": self.engine,
                "report": self.name,
                "startTime": self.start_time,
                "endTime": self.end_time,
                "timeZone": self.time_zone,
                "page": self.page,
                "pageSize": self.page_size,
                "groupBys": self.group_bys,
                "filters": self.filters,
                "projections": self.columns,
                }
        except ValueError as ex:
            self.last_error = ex
            return False

        return True


class Sprinklr:
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

        # current valid path options are (None), prod0, prod2, or sandbox
        if path is not None:
            if path.endswith("/"):
                self.path = path
            else:
                self.path = path + "/"
        else:
            self.path = ""
        logging.info("Client initialized. Path is " + self.path)

    def get_access_token(self, secret="", redirect_uri='', code=""):
        """
                Get Access Token based on code returned via authorization process
                :return: Dictionary of Dashboard columns
                """
        request_url = (f'https://api2.sprinklr.com/{self.path}oauth/token?'
                       f'client_id={self.key}&'
                       f'client_secret={secret}&'
                       f'redirect_uri={redirect_uri}&'
                       f'grant_type=authorization_code&'
                       f'code={code}')

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

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

        try:
            response = requests.post(url=request_url, headers=headers, data=json.dumps(data))
        except ConnectionError:
            self.status_message = "Connection Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except TimeoutError:
            self.status_message = "Timeout Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except requests.exceptions.RequestException:
            self.status_message = "Request Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)

        if response is not None:
            self.status_code = response.status_code
            self.raw = response.text
            self.result = json.loads(response.text)

        return self.status_code == HTTP_OK

    def get_request(self, request_url):
        headers = {'key': self.key,
                   'Authorization': "Bearer " + self.access_token}

        response = None

        logging.info("Requesting URL:" + request_url)
        try:
            response = requests.get(url=request_url, headers=headers)
        except ConnectionError:
            self.status_message = "Connection Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except TimeoutError:
            self.status_message = "Timeout Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except requests.exceptions.RequestException:
            self.status_message = "Request Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)

        if response is not None:
            self.status_code = response.status_code
            self.raw = response.text
            self.result = json.loads(response.text)

        return self.status_code == HTTP_OK

    def report_query(self, data):
        request_url = f' https://api2.sprinklr.com/{self.path}api/v1/reports/query'
        self.post_request(request_url, data)
        return self.status_code == HTTP_OK

    # def create_case(self, workflow, attachment, case_id = None,
    #                case_number = None, subject = None, description = None,
    #                 version = None, status = None, priority = None, case_type = None, external_case = None,
    #                 contact = None, due_date = None, summary = None, created_time = None, modified_time = None,
    #                 first_message_id = None):
    #
    #       request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case'
    # def get_case_by_number(self, case_number):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/case-numbers'
    #
    # def get_case_by_channel_case_id(self):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/channel-case-ids'
    #
    # def get_case_by_channel_case_number(self):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/channel-case-numbers'
    #
    # def get_case_by_case_id(self, case_id):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/{case_id}'
    #
    # def delete_case(self, case_id_or_number):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case'
    #
    # def asset_upload(self, content_type, upload_tracker_id, file_name):
    #     ßßrequest_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/upload'
    #
    # def asset_create(self):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam'
    #
    # def asset_search(self):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/search'
    #
    # def asset_read(self, asset_id):
    #     request_url = f'https://api2.sprinklr.com/{self.path}/api/v1/sam/[asset_id]'
    #
    # def asset_import(self, import_type, url, upload_tracker_id):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/importUrl'
    #
    # def asset_update(self, asset_id, name, description, asset_status, expiry_time):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/{asset_id}'
    #
    # def asset_delete(self, asset_id):
    #     request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/{asset_id}'

    def get_listening_insight_volume_trend(self, since_time, until_time,
                                           metric="MENTIONS", timezone_offset=0,
                                           dimension=None, filter_value=None):
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

    def request_all_dashboards(self):
        """
        request all dashboards
        :return: Dictionary of Engagement Dashboard
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/dashboards'

        self.get_request(request_url)
        return self.status_code == HTTP_OK

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

    def get_listening_topics(self):
        """
        request all listening topics
        :return: Dictionary of listening topics
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/listening/topics'

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

    def get_resources(self, types):

        request_url = f"https://api2.sprinklr.com/{self.path}api/v1/bootstrap/resources?types={types}"

        self.get_request(request_url)
        return self.status_code == HTTP_OK

    def get_report_metrics(self, report_engine, report_type):
        request_url = f"https://api2.sprinklr.com/{self.path}api/v1/reports/metadata/{report_engine}?{report_type}"

        self.get_request(request_url)
        return self.status_code == HTTP_OK

    def get_webhook_types(self):
        request_url = f"https://api2.sprinklr.com/{self.path}api/v2/webhook-subscriptions/webhook-types"
        
        self.get_request(request_url)
        return self.status_code == HTTP_OK
