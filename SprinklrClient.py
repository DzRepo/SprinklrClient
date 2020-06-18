import requests
import json
import urllib as urllib
import logging

HTTP_OK = 200
HTTP_NO_RESPONSE = 204

class SprinklrClient:
    """Sprinklr Client Library"""

    def __init__(self, key, path=None, access_token=None):
        """SprinklrClient

        Args:
            key (string): The API Key for the application, obtained at https://developer.sprinklr.com 
            path (string, optional): [description]. Defaults to None - Only necessary for environments other than Production.
            access_token (string, optional): Unique access token representing a user. Defaults to None, but needed most calls

            Most calls return a boolean indicating success or failure. It should not be necessary to wrap API calls in a try block.
            
            On success, the object will be returned in the .result property.
            If the return value is a JSON object(most common), it will be converted automatically to a Python dictionary object. the .raw property will 
            contain the text version of the response.

            On failure (return is false), status_message will contain the error text.

        """
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
        self.path = ""
        if path is not None:
            if path.endswith("/"):
                self.path = path
            else:
                self.path = path + "/"

# HTTP Methods

    def _make_api_request(self, verb, request_url, data = None, returns_json = True, is_file = False):
        
        headers = {'key': self.key,
                   'Authorization': "Bearer " + self.access_token}

        if verb.upper() in {"POST", "DELETE"}:
            headers['Content-Type'] = 'application/json'
            headers['cache-control'] = 'no-cache'

        if returns_json:
            headers['accept'] = 'application/json'

        if is_file:
            headers["Content-Type"] = 'multipart/form-data'

        logging.info(verb + " - URL:" + request_url)
        logging.debug("Headers:" + str(headers))

        response = None

        try:
            if verb.upper() == "GET":
                response = requests.get(url=request_url, headers=headers)
            elif verb.upper() == "DELETE":
                response = requests.delete(url=request_url, headers=headers, data=json.dumps(data))
            elif verb.upper() == "POST":
                # Detect if data is a JSON object and convert to string if necessary
                if type(data) is str:
                    response = requests.post(url=request_url, headers=headers, data=data)
                else:
                    response = requests.post(url=request_url, headers=headers, data=json.dumps(data))
            elif verb.upper() == "PUT":
                # Detect if data is a JSON object and convert to string if necessary
                if type(data) is str:
                    response = requests.put(url=request_url, headers=headers, data=data)
                else:
                    response = requests.put(url=request_url, headers=headers, data=json.dumps(data))
            else:
                raise ValueError("Verb must be one of Get, Delete, Post or Put")

            logging.debug(verb + " - Response code:" + str(response.status_code))
        except ConnectionError:
            logging.error(verb + " - Connection Error:" + request_url)
            self.status_message = "Connection Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except TimeoutError:
            logging.error(verb + " - Timeout Error:" + request_url)
            self.status_message = "Timeout Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except requests.exceptions.RequestException:
            logging.error(verb + " - Request Error:" + request_url)
            self.status_message = "Request Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)

        if response is not None:
            self.status_code = response.status_code
            self.raw = response.text
            if response.text.startswith("{"):
                self.result = json.loads(response.text)
            else:
                self.result = response.text

        if self.status_code not in {HTTP_OK, HTTP_NO_RESPONSE}:
            logging.error(verb + ' - Error response:' + response.text)
            self.status_message = response.text
            return False
        else:
            self.status_message = None
            return True

    def delete_request(self, request_url: str, data=None):
        """
        Supports all delete calls for API Endpoints.

        Args:
        request_url (string): API Endpoint
        data (JSON object): any data necessary to indicate object to be deleted

        Returns:
        boolean: True if call successful, False if not. On error/failure, status_message should contain information.
        """
        return self._make_api_request("DELETE", request_url, data)
        

    def get_request(self, request_url: str, returns_json=True):
        """ Supports all GET calls for API Endpoints.

        Args:
            request_url (string): API endpoint
            returns_json (bool, optional): indicates if response should be JSON encoded. If true, a header is set. Defaults to False.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
        """
        return self._make_api_request("GET", request_url)


    def post_request(self, request_url: str, data: object, is_file=False):
        """
        Supports all post calls for API Endpoints.

        Args:
        request_url (string): API Endpoint
        data (JSON object): any data necessary to indicate object to be posted
        is_file (bool, optional) indicates if data contains a filename that would be posted as data. Defaults to False

        Returns:
        boolean: True if call successful, False if not. On error/failure, status_message should contain information.
        """

        return self._make_api_request("POST", request_url, data = data, is_file=is_file)
        
    def put_request(self, request_url: str, data=None):
        """
        Supports all put calls for API Endpoints.

        Args:
        request_url (string): API Endpoint
        data (JSON object): any data necessary to indicate object to be updated

        Returns:
        boolean: True if call successful, False if not. On error/failure, status_message should contain information.
        """
        return self._make_api_request("PUT", request_url, data )


# Account 2.0
    def fetch_account_by_channel_id(self, account_type, channel_id):
        """
        Fetch the details of an account using an account type and channel id.

        Args:
        account_type (string): Type of account. e.g FACEBOOK, FBPAGE etc.
        channel_id: Unique id of the account on channel.

        Returns:
        boolean: True if call successful, False if not. On error/failure, status_message should contain information.
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/account/{account_type}/{channel_id}'
        return self.get_request(request_url, returns_json=True)

    def delete_account(self, account_id):
        """
        Deletes the sepecified account.

        Args:
        account_id (integer): The unique id of the account

        Returns:
        boolean: True if call successful, False if not. On error/failure, status_message should contain information.
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/account/{account_id}'
        return self.delete_request(request_url)

    def update_custom_properties(self, account_id, properties):
        """
        Updates the custom properties of an account.

        Args:
        account_id (integer): The unique id of the account
        properties: (JSON Dictionary) A collection of custom properties to update and thier new values

        Returns:
        boolean: True if call successful, False if not. On error/failure, status_message should contain information.
        """

        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/account/update/{account_id}/customProperties'
        return self.put_request(request_url, properties)

    def update_account_visibility(self, account_id, permissions):
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/account/{account_id}/visibility-permissions'
        return self.put_request(request_url, permissions)

# Authorize
    # this endpoint only returns the URL used to start the authorization process. It does not invoke the web-browser required workflow.
    def authorize(self, redirect_uri):
        """
        Generates a URL that can be used to start the authorization process.

        Args:
        redirect_uri (string): *must be the same redirect_uri stored in the application definition on https://developer.sprinklr.com *. 
        This is the URL where the temporary code will be sent as a URL parameter.

        Returns:
        string: URL used to initiate the authorization process
        """

        request_url = f'https://api2.sprinklr.com/{self.path}oauth/authorize?client_id={self.key}&response_type=code&redirect_uri={redirect_uri}'
        return request_url

    def fetch_access_token(self, secret=None, redirect_uri=None, code=None):
        """
        Generates an access token that can be used to make API calls on behalf of the user for an application.

        Args:
        secret (string): API key created at developer.sprinklr.com
        redirect_uri (string): *must be the same redirect_uri stored in the application definition on https://developer.sprinklr.com *. 
        code: The temporary code created via the user authentication process, sent to the redirect_uri 

        Note: This assumes the API Key has been set in the SprinklrClient object
        Returns:JSON dictionary of Access Token, Refresh Token and expire time (in seconds)
        """

        logging.info("Calling get_access_token")
        request_url = (f'https://api2.sprinklr.com/{self.path}oauth/token?'
                       f'client_id={self.key}&'
                       f'client_secret={secret}&'
                       f'redirect_uri={redirect_uri}&'
                       f'grant_type=authorization_code&'
                       f'code={code}')

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = None      
        verb = "POST (Authorize)"          
        try:
            response = requests.post(url=request_url, headers=headers)
        except ConnectionError:
            logging.error(verb + " - Connection Error:" + request_url)
            self.status_message = "Connection Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except TimeoutError:
            logging.error(verb + " - Timeout Error:" + request_url)
            self.status_message = "Timeout Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)
        except requests.exceptions.RequestException:
            logging.error(verb + " - Request Error:" + request_url)
            self.status_message = "Request Error"
            self.status_code = -1
            logging.exception(self.status_message, request_url)

        if response is not None:
            self.status_code = response.status_code
            self.raw = response.text
            if response.text.startswith("{"):
                self.result = json.loads(response.text)
            else:
                self.result = response.text

        if self.status_code not in {HTTP_OK, HTTP_NO_RESPONSE}:
            logging.error(verb + ' - Error response:' + response.text)
            self.status_message = response.text
            return False
        else:
            self.status_message = None
            self.encoding = response.encoding
            j_result = json.loads(response.content)
            self.access_token = j_result["access_token"]
            self.token_type = j_result["token_type"]
            self.refresh_token = j_result["refresh_token"]
            return True

    def refresh_access_token(self, secret, redirect_uri, refresh_token):
        """
        Regenerates an access token without requireing a UI validation Used if the Access Token has expired.

        Args:
        secret (string): Secondary Secret token created with Application Key - available on developer.sprinklr.com
        redirect_uri (string): must be the same redirect_uri for the application. Where the redirect will send the temporary code
        refresh_token (string): The token created at the same time as the Access Token during fetch_access_token

        Returns:JSON dictionary of Access Token, (new) Refresh Token and expire time (in seconds)
        """
        logging.info("Calling refresh_access_token")

        request_url = f'https://api2.sprinklr.com/{self.path}oauth/token?client_id={self.key}&client_secret={secret}&redirect_uri={redirect_uri}&grant_type=refresh_token&refresh_token={refresh_token}'
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

# Assets 1.0 & SAM

    def create_asset(self, asset_data):
        """
        Creates an asset within the Sprinklr Asset Manager. As a response, you will get the ID of the asset after making the request.

        Args:
            asset_data: JSON Object representing asset

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam'
        return self.post_request(request_url, asset_data)

    def delete_asset(self, asset_id):
        """
        Deletes an asset specified by the id. 

        Args:
            asset_data: JSON Object representing asset

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/{asset_id}'
        return self.delete_request(request_url, None)

    def import_asset(self, import_type, url, upload_tracker_id):
        """
        Imports an asset to the content store from an external link. The following content types are supported: IMAGE, VIDEO and LINK. 
        But uploading content to the content store does not mean that it is available in the Sprinklr Social Asset Manager. 
        After uploading content to the content store, use the Asset Create endpoint to create an asset in the Social Asset Manager.

        Args:
            import_type (string): Avalaible content types: IMAGE, VIDEO, LINK - If IMAGE or VIDEO is used, the content from the URL is imported. If LINK is used, a preview of the link is imported. 
            url ([type]): 	The URL of the asset you want to import. 
            upload_tracker_id ([type]): A unique identifier from the client.  This id is any string that you make up.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/importUrl?importType={import_type}&url={url}&uploadTrackerId={upload_tracker_id}'
        return self.post_request(request_url, None)

    def read_asset(self, asset_id):
        """
        Retrieves an asset from the Sprinklr Asset Manager, with a specific asset ID.

        Args:
            asset_id (string): The Id of the Asset on which you want to make a Read API call

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/{asset_id}'
        return self.get_request(request_url, returns_json=True)

    def search_asset(self, search_request):
        """
        Searches the content within the Assets.

        Args:
            search_request: (JSON object) - object formatted with search parameters 

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/search'
        return requests.post(request_url, search_request)

    def update_asset(self, asset_id, update_request):
        """
        Updates an asset within the SAM Assets. 
        The API only supports updating Digital Assets, Link Assets, and Text Assets. 
        It does not support updating Post Assets at this time.

        Args:
            update_request (JSON object): object formatted with the update parameters 

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/{asset_id}'
        return self.put_request(request_url, update_request)

    def asset_upload(self, content_type, upload_tracker_id, file_name):
        """
        Uploads content in the content store. 
        But uploading content to the content store does not mean it is available in the Sprinklr Social Asset Manager. 
        After uploading content to the content store, use the Asset Create endpoint to create an asset in the Social Asset Manager.

        Args:
            content_type (string): Avalaible content types are IMAGE, VIDEO, FILE.
            upload_tracker_id (string): A unique identifier from the client. This id is any string as long as it is unique each time.
            file_name (string): This is a form data parameter. The name of the file to upload.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/sam/upload?contentType={content_type}&uploadTrackerId={upload_tracker_id}'
        try:
            filedata = {'file': open(file_name)}
        except (Exception):
            self.status_message = {"Error - file not found"}
            return False
        else:
            return self.post_request(request_url, filedata, is_file=True)

# Assets 2.0

    def create_asset_group(self, asset_group):
        """
        Creates an Asset group.

        Args:
            asset_group (JSON object): object formatted with the asset group parameters 

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/asset-group'
        return self.post_request(request_url, asset_group)

    def fetch_asset_group(self, groupId):
        """
        Fetches an Asset group details and all related objects using group Id.

        Args:
            groupId (string): Id of the group.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/asset-group/{groupId}'
        return self.get_request(request_url, False)

    def update_asset_group(self, groupId, asset_update):
        """
        Updates an Asset group.

        Args:
            groupId (string): Id of the group.
            asset_update (JSON object): object formatted with the asset group parameters

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/asset-group/{groupId}'
        return self.put_request(request_url, asset_update)

    def delete_asset_group(self, groupId):
        """
        Deletes an Asset group.

        Args:
            groupId (string): Id of the group

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/asset-group/{groupId}'
        return self.delete_request(request_url)

# Audit

    def fetch_audit(self, request):
        """
        Fetches a collection of audit events for an object.
        The Audit API gives a full history of what/who has changed the object over time. 
        That's usually used for governance to trace down who has made what changes and when. 
        Make an Audit API POST call request and in the Body, enter a raw request in JSON format, 
        as the endpoint expects a JSON body which contains the details of the Asset Ids required to make an Audit API call.

        Args:
            request (JSON object): object formatted with the audit request parameters

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/audit/fetch'
        return self.post_request(request_url, request)

# Bootstrap
    def fetch_partner_campaigns(self):
        """
        Fetches a list of global campaigns in the partner environment 

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('PARTNER_CAMPAIGNS')

    def fetch_webhook_types(self):
        """
        Fetch all the available webhook subscription types. 

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f"https://api2.sprinklr.com/{self.path}api/v2/webhook-subscriptions/webhook-types"
        return self.get_request(request_url)

    def fetch_resources(self, types):
        """
        Fetches a collection of objects configured in the environment.

        Args:
            types (string): Type of resource to retrieve

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """

        request_url = f"https://api2.sprinklr.com/{self.path}api/v1/bootstrap/resources?types={types}"
        return self.get_request(request_url)

    def fetch_macros(self):
        """
        Fetches a collection of available macros.
        In the UI, macros can be used to execute multiple actions on a message, asset, or profile with a single click, creating workflow efficiencies.
        
        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('MACROS')

    def fetch_client_profile_lists(self):
        """
        Fetches a collection of client profiles.

        Args:
            None

          Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
      """
        return self.fetch_resources('CLIENT_PROFILE_LISTS')

    def fetch_partner_profile_lists(self):
        """
        Fetches a collection of profile lists in the client environment

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('PARTNER_PROFILE_LISTS')

    def fetch_client_queues(self):
        """
        Fetches a list of queues in the partner environment

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('CLIENT_QUEUES')

    def fetch_partner_queues(self):
        """
        Fetches a list of queues in the partner environment

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('PARTNER_QUEUES')

    def fetch_approval_paths(self):
        """
        Fetches a list of approval paths

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('APPROVAL_PATHS')

    def fetch_accessible_users(self):
        """
        Fetches a list of user profile information

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('ACCESSIBLE_USERS')

    def fetch_um_priorities(self):
        """
        Fetches a collection of priorities

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('UM_PRIORITIES')

    def fetch_um_statuses(self):
        """
        Fetches a collection of statuses
        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('UM_STATUSES')

    def fetch_partner_accounts(self):
        """
        Fetches a list of all active accounts in the partner 

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('PARTNER_ACCOUNTS')

# Campaigns 1.0

    def create_campaign_v1(self, campaign_data):
        """
        Creates a Campaign.

        Args:
            campaign_data (JSON object): Campaign definition

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}/api/v1/campaign'
        return self.post_request(request_url, campaign_data)

# Campaigns 2.0
    def create_campaign(self, campaign_data):
        """
        Creates a Campaign.

        Args:
            campaign_data (JSON object): object definition of a campaign

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/campaign'
        return self.post_request(request_url, campaign_data)

    def fetch_campaign(self, campaign_id):
        """
        Fetches a Campaign by it's Id.

        Args:
            campaign_id (string): Campaign Id for which you want to fetch details.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/campaign/{campaign_id}'
        return self.get_request(request_url)

    def update_campaign(self, campaign_id, campaign_data):
        """
        Updates a Campaign using the external source and source Id.

        Args:
            campaign_id (string): Campaign Id for which you want to update.
            campaign_data (JSON object): Campaign definition

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/campaign/{campaign_id}'
        return self.put_request(request_url, campaign_data)

    def delete_campaign(self, campaign_id):
        """
        Deletes a Campaign using campaign Id.

        Args:
            campaign_id (string): Campaign Id for which you want to delete

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/campaign/{campaign_id}'
        return self.delete_request(request_url)

    def create_external_campaign(self, campaign_data):
        """
        Creates a Campaign.

        Args:
            campaign_data (JSON object): Campaign definition

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/campaign'
        return self.post_request(request_url, campaign_data)

    def update_external_campaign(self, external_source, external_id, campaign_data):
        """
        Updates an external campaign.

        Args:
            external_source (string): Name of extenal source.
            external_id (string): Id of extenal source.
            campaign_data (JSON object): Campaign definition

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/campaign/{external_source}/{external_id}'
        return self.put_request(request_url, campaign_data)

    def fetch_external_campaign(self, external_source, external_id):
        """
        Fetches a campaign by external campaign details.

        Args:
            external_source (string): Name of extenal source
            external_id (string): Id of extenal source

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/campaign/{external_source}/{external_id}'
        return self.get_request(request_url)

    def delete_external_campaign(self, external_source, external_id):
        """
        Deletes an External Campaign using external Id and source.

        Args:
            external_source (string): Name of extenal source
            external_id (string): Id of extenal source

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/campaign/{external_source}/{external_id}'
        return self.delete_request(request_url)

# Case 1.0

    def create_case_v1(self, case_data):
        """
        Creates a case.
        A Sprinklr Case can be created.which allows you to track customer interactions as a bundled group of messages. 
        Once a Case has been created, subsequent responses can be kept together, organized as a single Case, 
        which can help streamline workflows, keep messages organized, and simplify reporting on customer interactions.

        Args:
            case_data (JSON object): object definition for a case 

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/case'
        return self.post_request(request_url, case_data)

    def delete_case_v1(self, case_id):
        """
        Creates a case.
        A Sprinklr Case can be created, which allows you to track customer interactions as a bundled group of messages. 
        Once a Case has been created, subsequent responses can be kept together, organized as a single Case, which can help streamline workflows, 
        keep messages organized, and simplify reporting on customer interactions.

        Args:
            case_id (string): unique identifier for case

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{{env}}/api/v1/case'
        return self.delete_request(request_url, )

    def search_case_v1(self, search_parameters):
        """
        Searches for cases with a variety of parameters.

        Args:
            search_parameters (JSON object): request search object

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/case/search'
        return self.post_request(request_url, search_parameters)

    def update_case_v1(self, case_data):
        """
        Updates a case. The updated case  get the updated case after making the Request.

        Args:
            case_data (JSON object): object definition for a case

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/case/update'
        return self.post_request(request_url, case_data)

# Case 2.0

    def create_case(self, case_data):
        """
        Creates a case.

        Args:
            case_data (JSON object): object definition for a case

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case'
        return self.post_request(request_url, case_data)

    def fetch_case_by_number(self, case_number):
        """
        Fetches a case by case number.

        Args:
            case_number (string): Case number of the case you want to fetch.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/case-numbers?case-number={case_number}'
        return self.get_request(request_url, returns_json=True)

    def fetch_case_by_channel_case_id(self, channel_case_id):
        """
        Fetches a case by channel case id.

        Args:
            channel_case_id (string): Channel case id of the case for which you want to run this API call.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/channel-case-ids?channelCaseIds={channel_case_id}'
        return self.get_request(request_url, returns_json=True)

    def fetch_case_by_channel_case_number(self, chanel_case_number):
        """
        Fetches a case by channel case number.

        Args:
            chanel_case_number (string): Channel case number of the case you want to fetch.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/channel-case-numbers?channelCaseNumbers={chanel_case_number}'
        return self.get_request(request_url, returns_json=True)

    def fetch_case_by_case_id(self, case_id):
        """
        Fetches a case by case id. 

        Args:
            case_id (string): Case Id of the case for which you want to fetch details.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/{case_id}'
        return self.get_request(request_url, returns_json=True)

    def fetch_case_associated_messages(self, case_id):
        """
        Fetches all the message ids associated with a case. 
        A cursor will also be returned to fetch all message ids associated with case after a certain time.

        Args:
            case_id (string): Id of the case for which you want fetch all associated messages.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case/associated-messages?id={case_id}'
        return self.get_request(request_url, returns_json=True)

    def delete_case(self, case_id):
        """
        Deletes a case by channel case number and case id.

        Args:
            case_id (string): Case Id or Case number of the case you want to delete

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        delete_url = f'https://api2.sprinklr.com/{self.path}api/v2/case'
        data = {case_id}
        return self.delete_request(delete_url, data)

    def update_case(self, case_data):
        """
        Updates a Case.

        Args:
            case_data (JSON object): object definition for a case.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/case'
        return self.put_request(request_url, case_data)

# Comment
    def search_comments(self, asset_id, asset_class):
        """
        Searches for Comments.

        Args:
            asset_id (string): The Id of the asset on which the comment search required.
            asset_class (string): Asset type - one of ( UNIVERSAL_CASE, MESSAGE_WORKFLOW, PROFILE_WORKFLOW, MEDIA_ASSET)

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/generic/comment/search/{asset_class}/{asset_id}'
        data = {
            "assetClass": asset_class,
            "assetId": asset_id
        }
        return self.post_request(request_url, data)

# Comment 2.0
    def add_comment(self, entity_type, entity_id, comment):
        """
        Adds a comment to different entity types.

        Args:
            entity_type (string): Type of Entity to add comment to - one of (MESSAGE, CASE, CAMPAIGN and PROFILE)
            entity_id (string): Entity id with respect to entity types.
            comment (string): Comment to add to the entity

         Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
       """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/comment/{entity_type}/{entity_id}'
        data = {"text": comment}
        return self.post_request(request_url, data)

    def fetch_comment(self, entity_type, entity_id, comment_id):
        """
        Fetches a comment from different entity types using entity Id and comment Id

        Args:
            entity_type (string): Type of Entity to fetch comment from - one of (MESSAGE, CASE, CAMPAIGN and PROFILE)
            entity_id (string): Entity id with respect to entity types.
            comment_id (string): Comment ID to fetch

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/comment/{entity_type}/{entity_id}/{comment_id}'
        return self.get_request(request_url)

# Custom Fields
    def create_custom_field(self, field_definition):
        """
        Creates a custom field.

        Args:
            field_definition (JSON object): Object defining the custom field

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/customfield'
        return self.post_request(request_url, field_definition)

    def search_custom_field(self, search_parameters):
        """
        Searches for a custom field with different parameters.

        Args:
            search_parameters (JSON object): Request object with search parameters

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/customfield/search'
        return self.post_request(request_url, search_parameters)

    def update_custom_field(self, field_id, field_definition):
        """
        Updates a custom field definition.

        Args:
            field_id (string): Unique identifier of custom field
            field_definition (JSON object): Object defining the custom field

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/customfield/{field_id}'
        return self.put_request(request_url, field_definition)

    def fetch_custom_field(self, field_id):
        """
        Fetches a custom field definition.

        Args:
            field_id (string): unique identifier of the custom field

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            No response object is returned if successful       
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/customfield/{field_id}'
        return self.get_request(request_url)

    def update_custom_field_options(self, field_id, field_options):
        """
        Adds, Deletes and Sets user defined values of a custom field. 
        In this call request, body/payload can be changed to perform three different tasks using the same API endpoint.

        Args:
            field_id (string): unique identifier of the custom field
            field_options (JSON object): object containing changes to options for custom field

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            No response object is returned if successful
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/customfield/{field_id}/updateOptions'
        return self.put_request(request_url, field_options)

    def fetch_profile_custom_fields(self):
        """
        Fetches a list of profile custom properties

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('PROFILE_CUSTOM_FIELDS')

    def fetch_account_custom_fields(self):
        """
        Fetches a list of account custom properties

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('ACCOUNT_CUSTOM_FIELDS')

    def fetch_media_asset_custom_fields(self):
        """
        Fetches a list of asset custom properties

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('MEDIA_ASSET_CUSTOM_FIELDS')

    def fetch_outbound_custom_fields(self):
        """
        Fetches a list of outbound custom properties

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('OUTBOUND_CUSTOM_FIELDS')

    def fetch_inbound_custom_fields(self):
        """
        Fetches a list of inbound custom properties

        Args:
            None
            
        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('INBOUND_CUSTOM_FIELDS')

# Email
    def send_email(self, account_id, from_email, subject, message):
        """
        Creates an inbound email message and ingests it into Sprinklr based on account Id. Used to bypass email account ingestion into care. 
        
        Args:
            account_id (string): Id of the email account the message will be sent through
            from_email (string): email address of sender
            subject (string): email subject
            message (string): email message body

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful no object is returned 
        """
        clean_message = message.replace("'", "\'")
        request_url = f"https://api2.sprinklr.com/{self.path}api/v2/email/create?aId={account_id}"
        email = {"from": from_email, "subject": subject, "body": clean_message}
        return self.post_request(request_url, email)

# Engagement Dashboard
    def fetch_all_dashboards(self):
        """
        Fetches list of monitoring dashboards with their columns and IDs

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/dashboards'
        return self.get_request(request_url)

    def fetch_dashboard_by_name(self, dashboard_name: str):
        """
        Fetches a dashboard's definition by dashboard name. The dashboard name will be URL encoded.

        Args:
            dashboard_name (string): Name of Dashboard (exact names can be retrieved via "fetch_all_dashboards")

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/dashboard/{urllib.parse.quote(dashboard_name)}'
        return self.get_request(request_url)

    def fetch_dashboard_stream(self, dashboard_id, start=0, rows=21,
                               since_date=None, until_date=None, sort='snCreatedTime%20desc'):
        """
        Fetches messages from a dashboard that meet the parameters passed in.

        Args:
            dashboard_id (string): [description]
            start (int, optional): [description]. Defaults to 0.
            rows (int, optional): [description]. Defaults to 21.
            since_date ([type], optional): [description]. Defaults to None.
            until_date ([type], optional): [description]. Defaults to None.
            sort (str, optional): [description]. Defaults to 'snCreatedTime%20desc'.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """

        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/stream/{dashboard_id}' \
            f'/feed?sort={sort}&rows={rows}&meta=true&start={start}'

        if since_date is not None:
            request_url += "&sinceDate=" + since_date

        if until_date is not None:
            request_url += "&untilDate=" + until_date

        return self.get_request(request_url)

# Extensions

    def create_extension(self, extension):
        """
        Creates an extension. An extension point defines the callback URL destinations to receive a pushed data payload from Sprinklr.

        Args:
            extension (undefined):

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/extension'
        return self.post_request(request_url, extension)

    def fetch_extension(self, id):
        """
        Fetches the definition of an extension by id.

        Args:
            id (undefined):

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/extension/{id}'
        return self.get_request(request_url)

    def update_extension(self, id, extension):
        """
        Updates the properties of an extension.

        Args:
            id (undefined):
            extension (undefined):

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/extension/{id}'
        return self.put_request(request_url, extension)

    def delete_extension(self, id):
        """
        Deletes an extension point.

        Args:
            id (string): Unique identifier of extension to delete

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/extension/{id}'
        return self.delete_request(request_url)
    
# Listening

    def fetch_listening_topics(self):
        """
        Fetches a list of all available configured topic groups and topics.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/listening/topics'
        return self.get_request(request_url)

    def fetch_listening_stream(self, stream):
        """
        Fetches the message stream associated with each message, containing the required information. It returns StreamWidgetResponse.

        Args:
            stream (JSON object): object representing parameters to fetch stream

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/listening/query/stream'
        return self.post_request(request_url, stream)

# Listening Widgets
    def fetch_listening_widget_data(self, search_request):
        """
        Fetches time-based metrics. Request should include the trendAggregationPeriod attribute which is used to specify the data aggregation interval.

        Args:
            search_request (JSON object): Request object formatted with appropriate parameters

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/listening/query/widget'
        return self.post_request(request_url, search_request)

# Message 1.0

    def fetch_message_conversation(self, conversation_data):
        """
        Fetches message conversation details of a Post with different source type and channels.

        Args:
            conversation_data (JSON object):

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/conversations/new/message-details'
        return self.post_request(request_url, conversation_data)

    def fetch_message_by_UMID(self, umid):
        """
        Fetches a message by the Universal Message Id.

        Args:
            umid (string): Universal Message Id

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/message/{umid}'
        return self.get_request(request_url)

# Message 2.0
    def fetch_message_by_id(self, message_id):
        """
        Fetch messages by message id.

        Args:
            message_id (undefined): Id of the message

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/message/byMessageId?messageId={message_id}'
        return self.get_request(request_url, returns_json=True)

# Paid Initiative
    def create_paid_initiative(self, api_link, initiative):
        """
        Creates a new paid initiative
        Sprinklr's Paid Media Advertising solution makes it easy to maximize the effectiveness of your advertising program.

        Args:
            api_link (string): (Undocumented Parameter)
            initiative (JSON object): Request object representing initiative

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}{api_link}/paid/entity/paidinitiative/create'
        self.post_request(request_url, initiative)

# Product
    def create_product(self, product):
        """
        Creates a product in Sprinklr Product Catalog. Return object will contain the new Sprinklr Product Id.

        Args:
            product (JSON object): Product definition object

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/product'
        return self.post_request(request_url, product)

    def delete_product(self, id):
        """
        Deletes a product.

        Args:
            id (string): Sprinklr Product Id

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/product/{id}'
        return self.delete_request(request_url)

    def search_product(self, search_request):
        """
        Returns a collection of products that match search criteria

        Args:
            search_request (JSON object): Object defining the search request

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/product/search'
        return self.post_request(request_url, search_request)

    def update_product(self, id, product):
        """
        Updates product details.

        Args:
            id (string): Sprinklr Product Id
            product (JSON object): Product definition object

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/product/{id}'
        return self.put_request(request_url, product)

# Profile 1.0

    def fetch_profile_conversation(self, sn_type, sn_user_id, since_date=None, until_date=None, start=None, rows=None):
        """
        Fetches a profile conversations using channel type and user Id

        Args:
            sn_type (string): Social network type (Channel name)
            sn_user_id (string): User Id of profile on social network
            start=0 (integer): First message to read
            rows=1 (integer): Number of messages to return
            since_date (long integer): date/time in ms since Unix Epoch
            until_date=None (long integer): date/time in ms since Unix Epoch

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/profile/conversations?snType={sn_type}&snUserId={sn_user_id}'
        if since_date is not None:
            request_url = request_url + "&sinceDate=" + since_date
        if until_date is not None:
            request_url = request_url + "&untilDate=" + until_date
        if start is not None:
            request_url = request_url + "&start=" + start
        if rows is not None:
            request_url = request_url + "&rows=" + rows

        return self.get_request(request_url)

    # Note: This API Endpoint is assumed to exist, but has not been tested and does not exist in the documentation.
    def add_profile_custom_field(self, custom_field):
        """
        You can update the values of profile custom properties on profiles.

        Args:
            custom_field: JSON Object of custom fields, values and profile IDs

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/profile/workflow/customProperties'
        return self.post_request(request_url, custom_field)

    def update_profile_custom_field(self, custom_field):
        """
        You can update the attributes of profile custom properties on profiles.

        Args:
            custom_field: JSON Object of custom fields, values and profile IDs

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/profile/workflow/customProperties'
        return self.put_request(request_url, custom_field)

    def replace_profile_custom_field(self, custom_field):
        """
        You can Update the values of profile custom properties on profiles.

        Args:
            custom_field: JSON Object of custom fields, values and profile IDs

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/profile/workflow/customProperties'
        return self.post_request(request_url, custom_field)

    def update_profile_list(self, client_id, profile_list):
        """
        Updates a profile list.

        Args:
            client_id: integer - The client id in which to make the changes
            profile_list: JSON Object of profile list changes

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/profile/workflow/profileList?clientId={client_id}'
        return self.post_request(request_url, profile_list)

    def fetch_profile(self, sn_type, sn_user_id):
        """
        Fetches profile details using channel type and user Id

        Args:
            sn_type (Integer): Integer - Channel Type for the message
            sn_user_id (Integer): - User Id of the channel

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/profile?snType={sn_type}&snUserId={sn_user_id}'
        return self.get_request(request_url)

    def search_profile(self, search_parameters):
        """
        Searches for matching profiles.

        Args:
            search_parameters (JSON object): Object representing the search parameters

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/profile/search'
        return self.post_request(request_url, search_parameters)

# Profile 2.0
    def fetch_profile_by_type_and_id(self, sn_type, sn_user_id):
        """
        Fetches a profile using snType and snUserId.

        Args:
            sn_type (Integer): Channel type for the profile
            sn_user_id (Integer): User Id of the user on the channel

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/profile?snType={sn_type}&snUserId={sn_user_id}'
        return self.get_request(request_url)\


    def search_profile_by_type_and_name(self, sn_type, user_name):
        """
        Searches for profiles matching snType and user name

        Args:
            sn_type (Integer): Channel type for the profile
            user_name (string): User name of the user on the channel (will be URL Encoded automatically)

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/profile/search?snType={sn_type}&userName={urllib.parse.quote(user_name)}'
        return self.get_request(request_url)

    def fetch_profile_by_id(self, profile_id):
        """
        Fetches a profile using profile id

        Args:

            profile_id (String): Profile Id of the profile, you want to fetch.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/profile/{profile_id}'
        return self.get_request(request_url)

    def create_update_universal_profile(self, profile):
        """
        Creates or updates a Universal Profile.

        Args:
            profile (JSON object): Object representing the profile to create or update

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/profile'
        return self.post_request(request_url, profile)

# Publishing 1.0
    def create_draft_post_v1(self, post):
        """
        Creates a Draft Post. It can be either an original post or a reply to existing post. The response will be the Message Id.

        Args:
            post (JSON object): Object representing the draft message

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/publishing/draft/new'
        return self.post_request(request_url, post)

    def post_draft_read_v1(self, message_id):
        """
        Fetches a Draft Message. After making the GET Request, you will get the Message Objects in JSON format as Response.

        Args:
            message_id (int): Unique id of the message to be retrieved

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/outbound/drafts?messageIds={message_id}'
        return self.get_request(request_url)

    def update_draft_post_v1(self, message_id, post):
        """
        You can update an existing draft post in the UI via this API call and you will get “HTTP/1.1 204 No Content” as Response after making the Request. 
        It can either be an original post or a reply. Make a PUT request and in the Body, enter the raw update request with the JSON format, 
        as the endpoint expects a JSON body which contains the details of the keys and values required to update a draft post.

        Args:

            message_id (string): Unique id of the message to be retrieved
            post (JSON object): Object representing the message

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/publishing/draft/{message_id}'
        return self.put_request(request_url, post)

    def publish_post_v1(self, post):
        """
        Schedules a Post for publishing. Post Id is returned on success.

        Args:
            post (JSON object): Object representing the message

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/publishing/post'
        return self.post_request(request_url, post)

# Publishing 2.0
    def create_draft_message(self, post):
        """
        You can create a Draft of a given message via this API call and you will get the Draft Message Id as Response after making the Request.

        Args:
            post: JSON Object representing the draft message

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/publishing/draft'
        return self.post_request(request_url, post)

    def schedule_draft_message(self, post):
        """
        You can schedule a draft of a given message via this API call and you will get the Schedule Draft Message Id as Response after making the Request.

        Args:
            post: JSON Object representing the draft message scheduling parameters

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/publishing/draft/schedule'
        return self.post_request(request_url, post)

    def update_draft_message(self, post):
        """
        You can Update a draft of a message.

        Args:
            post: JSON Object representing the draft message

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/publishing/draft/update'
        return self.put_request(request_url, post)

    def publish_message(self, post):
        """
        You can either reply to a message or send a new private message.

        Args:
            post: JSON Object representing the message and parameters for publishing

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/publishing/message'
        return self.post_request(request_url, post)

    def publish_post(self, post):
        """
        Schedules a given message.

        Args:
            post: JSON Object representing the message and parameters for publishing

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/publishing/post'
        return self.post_request(request_url, post)

    def publish_reply(self, post):
        """
        Either sends or schedules a reply to a message

        Args:
            post (JSON Object): representing the message and parameters for publishing

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/publishing/reply'
        return self.post_request(request_url, post)

# Reporting 1.0

    def fetch_report_v1(self, report_request):
        """
        Requests report results based on the passed in report query object.

        Args:
            report_request (JSON Object): Report Request object

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f' https://api2.sprinklr.com/{self.path}api/v1/reports/query'
        return self.post_request(request_url, report_request)

    def fetch_report_custom_metrics(self, report_engine):
        """
        Fetch the Custom Metrics for a given Report Engine.

        Args:
            report_engine (string): Name of the Report Engine (examples are "PLATFORM" and "PAID")

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/reports/customMetric/{report_engine}'
        return self.get_request(request_url)

    def fetch_report_metrics_and_dimensions(self, report_engine, report_type):
        """
        Fetch the Metrics and Dimensions available for a given Report Engine and Report Type (name).

        Args:
            report_engine (string): Name of the Report Engine (examples are "PLATFORM" and "PAID")
            report_type (string): Name of the Report 

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/reports/metadata/{report_engine}?{report_type}'
        return self.get_request(request_url)

# Reporting 2.0

    def fetch_report(self, report_request):
        """
        Requests report results based on the passed in report query object (API 2.0 version).

        Args:
            report_request (JSON Object): Report Request object

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/reports/query'
        return self.post_request(request_url, report_request)

# Search

    def search_entity(self, entity_type, filter, sort_order='ASC', sort_key='id', page_size=0):
        """
        You can use the Search API to fetch data on the basis of entity types using filters.
        This is the main search_entity call. There are individual methods for each entity type defined as well.

        Args:
            entity_type (string): Supported entity types: CASE, CAMPAIGN, SAM.
            filter (JSON object): Filter object that defines the parameters of the search
            sort_order (optional, string): Defaults to Ascending, order of returned objects
            sort_key (optional, string): Defaults to 'id'
            page_size=0 (optional, int): Defailts to zero (returns default allowed by API)

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_case_next
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/search/{entity_type}'

        result = self.post_request(request_url, filter)
        if (result):
            self.search_cursor = self.result["data"]["cursor"]
        else:
            self.search_cursor = None
        return result

    def search_next_page(self, entity_type):
        """
        Retrieves the next page of search results.

        Args:     
            entity_type (string): Supported entity types: CASE, CAMPAIGN, SAM.

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_case_next
        """
        if self.search_cursor is not None:
            request_url = f'https://api2.sprinklr.com/{self.path}api/v2/search/{entity_type}?id={self.search_cursor}'
            result = self.get_request(request_url)
            if (result):
                self.search_cursor = self.result["data"]["cursor"]
            else:
                self.search_cursor = None
            return result
        else:
            self.status_message = {"error": "Search cursor not set"}
            return False  # no cursor

    def search_campaign(self, filter,  sort_order='ASC', sort_key='name', page_size=20):
        """
        Searches for Campaigns based on filters.

        Args:
            filter (JSON object): Filter object that defines the parameters of the search
            sort_order (optional, string): Defaults to Ascending, order of returned objects
            sort_key (optional, string): Defaults to 'name'
            page_size=0 (optional, int): Defailts to 20

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_case_next
        """
        return self.search_entity('CAMPAIGN', filter, sort_order, sort_key, page_size)

    def search_more_results(self):
        """
        Indicates if the previous search has additional results that can be retrieved

        Args:
            None

        Returns:
            boolean: True if additional results exist, False if not.
        """
        return self.search_cursor is not None

    def search_campaign_next(self):
        """
        Retrieves the next set of results from a campaign search.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_case_next
        """
        return self.search_next_page("CAMPAIGN")

    def search_case(self, filter,  sort_order='ASC', sort_key='id', page_size=20):
        """
        Searches for Campaigns based on filters.

        Args:
            filter (JSON object): Filter object that defines the parameters of the search
            sort_order (optional, string): Defaults to Ascending, order of returned objects
            sort_key (optional, string): Defaults to 'id'
            page_size=0 (optional, int): Defailts to 20

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_case_next
        """
        return self.search_entity('CASE', filter, sort_order, sort_key, page_size)

    def search_case_next(self):
        """
        Retrieves the next set of results from a case search.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_case_next
        """
        return self.search_next_page("CASE")

    def search_message(self, filter, sort_order='ASC', sort_key='id', page_size=20):
        """
        Searches for Messages based on filters.

        Args:
            filter (JSON object): Filter object that defines the parameters of the search
            sort_order (optional, string): Defaults to Ascending, order of returned objects
            sort_key (optional, string): Defaults to 'id'
            page_size=0 (optional, int): Defailts to 20

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_message_next
        """
        return self.search_entity('MESSAGE', filter, sort_order, sort_key, page_size)

    def search_message_next(self):
        """
        Retrieves the next set of results from a message search.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_message_next
        """
        return self.search_next_page("MESSAGE")

    def search_sam(self, filter, sort_order='ASC', sort_key='name', page_size=20):
        """
        Searches for Assets based on filters.

        Args:
            filter (JSON object): Filter object that defines the parameters of the search
            sort_order (optional, string): Defaults to Ascending, order of returned objects
            sort_key (optional, string): Defaults to 'name'
            page_size=0 (optional, int): Defailts to 20

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_sam_next
        """
        return self.search_entity('SAM', filter, sort_order, sort_key, page_size)

    def search_sam_next(self):
        """
        Retrieves the next set of results from an Asset search.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
            If a cursor exists, SprinklrClient.search_cursor is set to the URL that can be used to obtain the next set of results via search_sam_next
        """
        return self.search_next_page("SAM")

# Short URL

    def fetch_client_url_shortners(self):
        """
        Fetches a list of client URL shortners.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('CLIENT_URL_SHORTNERS')

    def create_short_url(self, shortner_id, link):
        """
        Given a long URL, returns a shortened URL.

        Args:
            shortner_id (int): Unique identifier of shortner (found via fetch_client_url_shortners())
            link (string): the long URL to be shorten

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/link/shorten'
        post_data = {
            "link": {link},
            "urlShortnerId": {shortner_id}
        }
        return self.post_request(request_url, post_data)

# Users
    def fetch_user(self):
        """
        Fetches user details of the user who authorized the passed access token.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v2/me'
        return self.get_request(request_url)

    def fetch_user_by_id(self, user_id):
        """
        Fetches user details by user Id.

        Args:
            user_id (int): Unique Sprinklr user id

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        

        """
        request_url = f'https://api2.sprinklr.com/{self.path}api/v1/scim/v2/Users/{user_id}'
        return self.get_request(request_url)

    def fetch_user_groups(self):
        """
        Fetches a list of user groups.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('USER_GROUPS')

    def fetch_permissions(self):
        """
        Fetches available permission combinations per platform area. Permissions regulate user authorization via the UI.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('PERMISSIONS')

    def fetch_clients(self):
        """
        Returns a list of clients provisioned in the partner. Clients are partitions with a Sprinklr Partner environment.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('CLIENTS')

    def fetch_client_users(self):
        """
        Fetches a list of all local users in the client environment.

        Args:
            None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('CLIENT_USERS')

    def fetch_partner_users(self):
        """
        Returns a list of all users in the partner environment.

        Args:
           None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object        
        """
        return self.fetch_resources('PARTNER_USERS')

    def fetch_partner_account_groups(self):
        """ Returns a list of Partner Account Groups

        Args:
           None

        Returns:
            boolean: True if call successful, False if not. On error/failure, status_message should contain information.
            If successful, SprinklrClient.result will contain a JSON object
        """        
        return self.fetch_resources('PARTNER_ACCOUNT_GROUPS')
        