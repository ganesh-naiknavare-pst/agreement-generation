from typing import Annotated
import uuid
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]


class AgreementState:
    def __init__(self):
        self.owner_id = str(uuid.uuid4())
        self.owner_name = ""
        self.tenants = {}
        self.tenant_names = {}
        self.owner_approved = False
        self.agreement_text = ""
        self.owner_signature = ""
        self.tenant_signatures = {}

    def add_tenant(self, tenant_email, tenant_name):
        tenant_id = str(uuid.uuid4())
        self.tenants[tenant_id] = False
        self.tenant_signatures[tenant_id] = ""
        self.tenant_names[tenant_id] = tenant_name
        return tenant_id

    def set_owner(self, owner_name):
        self.owner_name = owner_name

    def is_fully_approved(self):
        return self.owner_approved and all(self.tenants.values())


agreement_state = AgreementState()
