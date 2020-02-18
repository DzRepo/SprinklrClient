# SprinklrClient
A Python client library (SDK) for interacting with Sprinklr's REST API

**Notes:**
- See the [Generating an Access Token](Sprinklr%20Client%20Library%20-%20Generating%20an%20Access%20Token.pdf) document for directions after registering for a developer account at [Developer.Sprinklr.com](https://developer.sprinklr.com).

- Make sure the Sprinklr.conf file is kept safe! 
  - This file (if the SprinklrClientTest.py app is used) stores API Keys and Access Tokens. With these keys any API call can be made on your behalf. DO NOT under any circumstances upload these files to the public Internet. 
  - BEST PRACTICE: Add *.conf to your .gitignore file

- The Case Create & Update, and Asset Search functions have not been tested yet and may not work.

- The Report examples (other than Audit) may not work as is as they will need customizing to unique customer environments (filters). Follow the example in the [Sprinklr Reporting Widget Tutorial](https://developer.sprinklr.com/docs/read/api_tutorials/Sprinklr_Reporting_Widget_Tutorial), translating values as necessary.

Here is a list of current supported functions via the test client ([SprinklrClientTest.py](SprinklrClientTest.py)):

```
SprinklrClientTest Authorize {apikey} {redirect_uri}
                   AssetSearch [One | Two | Three]
                   CreateCase <-- Probably doesn't work
                   FetchAccessToken {apikey} {secret} {code} {redirect uri}
                   FetchAccessibleUsers
                   FetchAccountCustomFields
                   FetchAllDashboards
                   FetchCaseByNumber {case_number}
                   FetchCaseMessagesById {case_id}
                   FetchClients
                   FetchClientProfileLists
                   FetchClientUrlShortners
                   FetchClientUsers
                   FetchDashboardByName {name}
                   FetchDashboardStream {stream_id} {start} {rows} [{echo request} (True or False)]
                   FetchInboundCustomFields
                   FetchListeningTopics
                   FetchListeningStream {id} {sinceTime} {untilTime}
                   FetchMacros
                   FetchMediaAssetCustomFields
                   FetchMessageByIdAndSource {message_id} [ACCOUNT | PERSISTENT_SEARCH | LISTENING | BENCHMARKING | AUDIENCE | AUDIENCE_STUDY]}
                   FetchOutboundCustomFields
                   FetchPartnerAccountGroups
                   FetchPartnerAccounts
                   FetchPartnerCampaigns
                   FetchPartnerUsers
                   FetchPermissions
                   FetchProfileCustomFields
                   FetchReport LOCATION | CATEGORIES | ATTRIBUTES | REVIEWS | AUDIT
                   FetchReportMetrics {Report_Engine} {Report_Type}
                   FetchResources {resource type}
                   FetchUMPriorities
                   FetchUMStatuses
                   FetchUser
                   FetchUserById {User_Id}
                   FetchUserGroups
                   FetchWebhookTypes
                   RefreshAccessToken

Please let me know if you are using this library and send feedback to SteveDz@Sprinklr.com - Thanks!

Dz
