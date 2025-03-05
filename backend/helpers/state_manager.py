from typing import Annotated
import uuid
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


class AgreementState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.owner_id = str(uuid.uuid4())
        self.owner_name = ""
        self.owner_email = ""
        self.tenants = {}
        self.tenant_names = {}
        self.tenant_emails = {}
        self.owner_approved = False
        self.agreement_text = ""
        self.owner_signature = ""
        self.tenant_signatures = {}
        self.owner_photo = ""
        self.tenant_photos = {}
        self.pdf_file_path = ""
        self.is_pdf_generated = False

    def add_tenant(
        self, tenant_email, tenant_name, tenant_signature=None, tenant_photo=None
    ):
        tenant_id = str(uuid.uuid4())
        self.tenants[tenant_id] = False
        self.tenant_signatures[tenant_id] = tenant_signature
        self.tenant_photos[tenant_id] = tenant_photo
        self.tenant_names[tenant_id] = tenant_name
        self.tenant_emails[tenant_id] = tenant_email
        return tenant_id

    def set_owner(self, owner_name, owner_email=None):
        self.owner_name = owner_name
        if owner_email:
            self.owner_email = owner_email

    def is_fully_approved(self):
        return self.owner_approved and all(self.tenants.values())


agreement_state = AgreementState()

class TemplateAgreementState:
    def __init__(self):
        self.participant_id = str(uuid.uuid4())
        self.authority_id = str(uuid.uuid4())
        self.participant_approved = False
        self.authority_approved = False
        self.agreement_text = ""
        self.participant_signature = ""
        self.authority_signature = ""
        self.pdf_file_path = ""
        self.template_file_path = ""
        self.is_pdf_generated = False

    def is_fully_approved(self):
        return self.participant_approved and self.authority_approved

template_agreement_state = TemplateAgreementState()
