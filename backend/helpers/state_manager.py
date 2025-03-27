from typing import Annotated, Dict, Optional
import uuid
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from dataclasses import dataclass, field


class State(TypedDict):
    messages: Annotated[list, add_messages]
    agreement_id: int


@dataclass
class AgreementState:
    owner_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    owner_name: str = ""
    owner_email: str = ""
    tenant_emails: Dict[str, Optional[str]] = field(default_factory=dict)
    tenants: Dict[str, bool] = field(default_factory=dict)
    tenant_names: Dict[str, str] = field(default_factory=dict)
    owner_approved: bool = False
    agreement_text: str = ""
    owner_signature: str = ""
    tenant_signatures: Dict[str, Optional[str]] = field(default_factory=dict)
    owner_photo: str = ""
    tenant_photos: Dict[str, Optional[str]] = field(default_factory=dict)
    pdf_file_path: str = ""
    is_pdf_generated: bool = False
    agreement_id: Optional[int] = None

    def reset(self) -> None:
        """Resets the agreement state to its default values."""
        self.__init__()

    def add_tenant(self, tenant_email: str, tenant_name: str) -> str:
        """Adds a new tenant to the agreement."""
        tenant_id = str(uuid.uuid4())
        self.tenants[tenant_id] = False  # False indicates not yet approved
        self.tenant_names[tenant_id] = tenant_name
        self.tenant_emails[tenant_id] = tenant_email
        return tenant_id

    def update_tenant(self, tenant_signature: str, tenant_photo: str, tenant_id: str):
        self.tenant_signatures[tenant_id] = tenant_signature
        self.tenant_photos[tenant_id] = tenant_photo

    def set_owner(self, owner_name: str, owner_email: str) -> None:
        """Sets the owner's name."""
        self.owner_name = owner_name
        self.owner_email = owner_email

    def is_fully_approved(self) -> bool:
        """Checks if the agreement is fully approved."""
        return self.owner_approved and all(self.tenants.values())


@dataclass
class TemplateAgreementState:
    authority_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    participant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    authority_email: str = ""
    participant_email: str = ""
    authority_approved: bool = False
    participant_approved: bool = False
    agreement_text: str = ""
    authority_signature: str = ""
    participant_signature: str = ""
    pdf_file_path: str = ""
    template_file_path: str = ""
    is_pdf_generated: bool = False
    agreement_id: Optional[int] = None

    def reset(self) -> None:
        """Agreement state to its default values."""
        self.__init__()

    def set_authority(self, authority_email):
        self.authority_email = authority_email

    def set_participant(self, participant_email):
        self.participant_email = participant_email

    def is_fully_approved(self) -> bool:
        """Checks if the agreement is fully approved."""
        return self.participant_approved and self.authority_approved


class StateManager:
    def __init__(self):
        self._agreement_states: Dict[int, AgreementState] = {}
        self._template_agreement_states: Dict[int, TemplateAgreementState] = {}
        self._current_agreement_id: Optional[int] = None
        self._current_template_agreement_id: Optional[int] = None

    def get_agreement_state(self, agreement_id: int) -> AgreementState:
        if agreement_id not in self._agreement_states:
            state = AgreementState()
            state.agreement_id = agreement_id
            self._agreement_states[agreement_id] = state
        return self._agreement_states[agreement_id]

    def get_template_agreement_state(self, agreement_id: int) -> TemplateAgreementState:
        if agreement_id not in self._template_agreement_states:
            state = TemplateAgreementState()
            state.agreement_id = agreement_id
            self._template_agreement_states[agreement_id] = state
        return self._template_agreement_states[agreement_id]

    def cleanup_agreement_state(self, agreement_id: int) -> None:
        if agreement_id in self._agreement_states:
            del self._agreement_states[agreement_id]

    def cleanup_template_agreement_state(self, agreement_id: int) -> None:
        if agreement_id in self._template_agreement_states:
            del self._template_agreement_states[agreement_id]

    def set_current_agreement_id(self, agreement_id: int) -> None:
        self._current_agreement_id = agreement_id

    def set_current_template_agreement_id(self, agreement_id: int) -> None:
        self._current_template_agreement_id = agreement_id


# Create a singleton instance
state_manager = StateManager()
