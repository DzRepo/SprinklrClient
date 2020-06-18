# SprinklrClient
A simple Python client library (SDK) for interacting with Sprinklr's REST API

**Notes:**
- This library is not created by, or supported by Sprinklr.
Please review the library before using in a production environment to make sure it meets your organization's security and compliance requirements!

Installation now available via PyPi: 

```pip install SprinklrClient```


- See the [Generating an Access Token](Sprinklr%20Client%20Library%20-%20Generating%20an%20Access%20Token.pdf) document for directions after registering for a developer account at [Developer.Sprinklr.com](https://developer.sprinklr.com).

Please let me know if you are using this library. Send feedback to SteveDz@Sprinklr.com - Thanks!

Sample usage:

```
Python 3.7.6 (default, Jan  8 2020, 13:42:34)
[Clang 4.0.1 (tags/RELEASE_401/final)] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import SprinklrClient as sc
>>> client = sc.SprinklrClient("YOUR API KEY HERE", None, "YOUR ACCESS TOKEN HERE")
>>> client.add_comment("CASE", "75613", "Adding this note to a case!")
True
>>> client.fetch_webhook_types()
True
>>> webhook_types = client.result["data"]
>>> for webhook_type in webhook_types:
...     print(webhook_type['label'])
...
Audience Activity
Campaign Created
Campaign Deleted
Campaign Updated
Case Created
Case Deleted
Case Updated
Message Association Change
Comment Created
Comment Updated
Draft Created
Draft Scheduled
Draft Updated
Message Deleted
Message Delivered
Message Engagement Updated
Message Publish Failed
Message Published
Message Read
Message Received
Message Sent For Approval
Message Updated
Profile Created
Profile Deleted
Profile Updated
Profiles Merged
Asset Created
Asset Deleted
Asset Updated
Task Create
Task Delete
Task Update
Thread Control Updated
User Create
User Update
Workflow Updated
>>>
```

