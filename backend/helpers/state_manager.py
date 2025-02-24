from typing import Annotated
import uuid
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]


class AgreementState:
    def __init__(self):
        self.tenant_id = str(uuid.uuid4())
        self.owner_id = str(uuid.uuid4())
        self.tenant_approved = False
        self.owner_approved = False
        self.agreement_text = ""
        self.tenant_signature = ""
        self.owner_signature = ""

    def is_fully_approved(self):
        return self.tenant_approved and self.owner_approved

agreement_state = AgreementState()
