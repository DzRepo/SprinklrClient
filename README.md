# SprinklrClient
A simple Python client for interacting with Sprinklr's REST API

**Notes:**
- After registering for a developer account at [Developer.Sprinklr.com](https://developer.sprinklr.com), creating an app and authorizing it to a Sprinklr account as outlined in the [Getting Started](https://developer.sprinklr.com/docs/read/api_overview/Getting_Started) tutorial, the GetAccessToken command of SprinklrClientTest.py can be used to retrieve and store the AccessToken, RefreshToken and key to a .conf file for use by the other API examples. Make sure the Sprinklr.conf file is kept safe!

- The Case Create & Update, and Asset Search functions are not tested and most likely do not work.

- The Report examples  (other than Audit) will not work as is as they will need customizing to unique customer environments. Follow the example in the [Sprinklr Reporting Widget Tutorial](https://developer.sprinklr.com/docs/read/api_tutorials/Sprinklr_Reporting_Widget_Tutorial), translating values as necessary.

Current Supported Functions via the client:

```
SprinklrClientTest Authorize {apikey} {redirect_uri}
                   AssetSearch [One | Two | Three]
                   CreateCase
                   GetAccessToken {apikey} {secret} {code} {redirect uri}
                   GetAccessibleUsers
                   GetAccountCustomFields
                   GetAllDashboards
                   GetCaseByNumber {case_number}
                   GetCaseMessagesById {case_id}
                   GetClients
                   GetClientProfileLists
                   GetClientUrlShortners
                   GetClientUsers
                   GetDashboardByName {name}
                   GetDashboardStream {stream_id} {start} {rows} [{echo request} (True or False)]
                   GetInboundCustomFields
                   GetListeningTopics
                   GetListeningStream {id} {sinceTime} {untilTime}
                   GetMacros
                   GetMediaAssetCustomFields
                   GetMessageByIdAndSource {message_id} [ACCOUNT | PERSISTENT_SEARCH | LISTENING | BENCHMARKING | AUDIENCE | AUDIENCE_STUDY]}
                   GetOutboundCustomFields
                   GetPartnerAccountGroups
                   GetPartnerAccounts
                   GetPartnerCampaigns
                   GetPartnerUsers
                   GetPermissions
                   GetProfileCustomFields
                   GetReport LOCATION | CATEGORIES | ATTRIBUTES | REVIEWS | AUDIT
                   GetReportMetrics {Report_Engine} {Report_Type}
                   GetResources {resource type}
                   GetUMPriorities
                   GetUMStatuses
                   GetUser
                   GetUserById {User_Id}
                   GetUserGroups
                   GetWebhookTypes
                   RefreshAccessToken

Please let me know if you are using this library and send feedback to SteveDz@Sprinklr.com - Thanks!

Dz