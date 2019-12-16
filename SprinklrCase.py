class CaseBase:
    def __init__(self):
        self.case_id = None #
        self.case_number = None #
        self.subject = None # 
        self.description = None #
        self.status = None
        self.due_date = None
        self.request = None


class CaseCreate(CaseBase):
    def __init__(self):
        self.version = None #
        self.priority = None
        self.case_type = None
        self.__external_case = None
        self.__workflow = None
        self.__contact = None
        self.__attachment = None
        self.summary = None
        self.created_time = None
        self.modified_time = None
        self.first_message_id = None
                
    @property
    def external_case(self):
        return {
            "id" : self.__external_case.id,
            "caseNumber" : self.__external_case.case_number,
            "channelType" : self.__external_case.channel_type,
            "permalink" : self.__external_case.permalink,
            "createdTime" : self.__external_case.created_time,
            "modifiedTime" : self.__external_case.modified_time
        }
    
    @external_case.setter
    def external_case(self, ec):
        self.__external_case = ec

    @external_case.deleter
    def external_case(self):
        del self.__external_case


    class External_Case:
        def __init__(self, case_id, case_number, channel_type = None, permalink = None, created_time = None, modified_time = None):
            self.case_id = case_id
            self.case_number = case_number
            self.channel_type = channel_type
            self.permalink = permalink
            self.created_time = created_time
            self.modified_time = modified_time

    class Workflow:
        def __init__(self):
            self.__assignment = None
            self.modified_time = None
            self.custom_fields = {}
            self.queues = []
            self.space_workflows = []
            self.campaign_id = None

        class Assignment:
            def __init__(self, assignee_id, assignee_type, assigned_by_id, assigment_time):
                self.assignee_id = assignee_id
                self.assignee_type = assignee_type
                self.assigned_by_id = assigned_by_id
                self.assignment_time = assigment_time

        @property
        def assignment(self):
            return {
                "assigneeId" : self.__assignment.assignee_id,
                "assigneeType" : self.__assignment.assignee_type,
                "assignedById" : self.__assignment.assigned_by_id,
                "assignmentTime" : self.__assignment.assignment_time
            }

        @assignment.setter
        def assignment(self, assignment):
            self.__assignment = assignment

        @assignment.deleter
        def assignment(self):
            del self.__assignment

        class Queue:
            def __init__(self, queue_id, assignment_time):
                self.queue_id = queue_id
                self.assignment_time = assignment_time
        
        def add_queue(self, queue : Queue):
            self.queues.append({
                "queueId" : queue.queue_id,
                "assignmentTime" : queue.assignment_time
            })

        class SpaceWorkflow:
            def __init__(self, space_id, modified_time):
                self.space_id = space_id
                self.modified_time = modified_time
                self.custom_fields = {}
                self.queues = []

            def add_custom_field(self, property_name, name):
                self.custom_fields[property_name] = [ name ]

            def add_queue(self, queue_id, assignment_time):
                self.queues.append({
                    "queueId" : queue_id,
                    "assignmentTime" : assignment_time
                })

        def add_space_workflow(self, space_workflow : SpaceWorkflow):
            self.space_workflows.append({
                    "spaceId" : space_workflow.space_id,
                    "modifiedTime" : space_workflow.modified_time,
                    "customFields" : space_workflow.custom_fields,
                    "queues" : space_workflow.queues
            })

    @property
    def workflow(self):
        return {
            "assignment" : self.__workflow.assignment,
            "modifiedtime" : self.__workflow.modified_time,
            "customFields" : self.__workflow.custom_fields,
            "queues": self.__workflow.queues,
            "spaceWorkflows" : self.__workflow.space_workflows,
            "campaignId" : self.__workflow.campaign_id
        }
        

    @workflow.setter
    def workflow(self, wf):
        self.__workflow = wf

    @workflow.deleter
    def workflow(self):
        del self.__workflow
    

    class Contact:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    @property
    def contact(self):
        return {
            "id" : self.__contact.id,
            "name" : self.__contact.name,
        }

    @contact.setter
    def contact(self, contact):
        self.__contact = contact

    @contact.deleter
    def contact(self):
        del self.__contact
    

    class Attachment:
        def __init__(self, type):
            self.type = type
            self.attachment_options = []

        class Attachment_Option:
            def __init__(self, channel_type, account_id):
                self.channel_type = channel_type
                self.account_id = account_id

        def add_option(self, option : Attachment_Option):
            self.attachment_options.append({
                "channelType": option.channel_type,
                "accountId" : option.account_id
            })

    @property
    def attachment(self):
        return {
            "type" : self.__attachment.type,
            "attachmentOptions" : self.__attachment.attachment_options
        }

    @attachment.setter
    def attachment(self, attachment):
        self.__attachment = attachment

    @attachment.deleter
    def attachment(self):
        del self.__attachment

    def build_request(self):
        self.request = {
                "subject": self.subject,
                "description": self.description,
                "version": self.version,
                "status": self.status,
                "priority": self.priority,
                "caseType": self.case_type,
                "externalCase": self.external_case,
                "workflow": self.workflow,
                "contact": self.contact,
                "attachment": self.attachment,
                "dueDate": self.due_date,
                "summary": self.summary,
                "createdTime": self.created_time,
                "modifiedTime": self.modified_time,
                "firstMessageId": self.first_message_id
                }
        if self.case_id is not None:
            self.request["caseIds"] =  self.case_id
        if self.case_number is not None:
            self.request["caseNumbers"] = self.case_number
        if self.priority is not None:
            self.request["priority"] = self.priority
        if self.case_type is not None:
            self.request["caseType"] = self.case_type
        if self.external_case is not None:
            self.request["externalCase"] = self.external_case
        if self.workflow is not None:
            self.request["workflow"] = self.workflow
        if self.contact is not None:
            self.request["contact"] = self.contact
        if self.attachment is not None:
            self.request["attachment"] = self.attachment
        if self.summary is not None:
            self.request["summary"] = self.summary
        if self.created_time is not None:
            self.request["createdTime"] = self.created_time
        if self.modified_time is not None:
            self.request["modifiedTime"] = self.modified_time



class CaseUpdate(CaseBase):
    def __init__(self):
        self.assiged_to = None
        self.case_id = None
        self.case_number = None
        self.due_date = None
        self.update_custom_fields_in_crm = None
        self.added_notify_users = None
        self.removed_notify_users = None
        self.synced_notify_usrs = None
        self.update_actions = []      
        self.added_custom_properties = None
        self.removed_custom_properties = None
        self.synced_custom_properties = None
        self.synced_selected_custom_properties = None
        self.synced_channel_custom_properties = None
        self.disassociate_case_ids = None
        self.installed_app_id = None
        self.installed_app_org_id = None
        self.installed_app_user_id = None
        self.application_user_id = None
        self.channel_type = None
        self.channel_case_id = None
        self.channel_case_number = None
        self.channel_owner_id = None
        self.channel_case_created_time = None
        self.channel_case_modified_time = None
        self.permalink = None
        self.additional_information = None

    def build_update_request(self):

        # required fields we know they're there
        self.request = {
                "dueDate": self.due_date,
                "updateCustomFieldsInCRM" : self.update_custom_fields_in_crm
        }

        #optional fields
        if self.case_id is not None:
            self.request["caseIds"] =  self.case_id
        if self.case_number is not None:
            self.request["caseNumbers"] = self.case_number
        if self.assiged_to is not None:
            self.request["assignedTo"] = self.assiged_to
        if self.subject is not None:
            self.request["subject"] = self.subject
        if self.description is not None:
            self.request["description"] = self.description
        if self.status is not None:
            self.request["status"] = self.status

        
        