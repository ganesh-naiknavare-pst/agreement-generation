from typing import Annotated, Dict, Optional, List
import uuid
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from dataclasses import dataclass, field
from datetime import datetime


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
    property_address: str = ""
    city: str = ""
    rent_amount: int = 0
    agreement_period: List[datetime] = field(default_factory=list)
    owner_address: str = ""
    tenant_details: list[dict] = field(default_factory=list)
    furnishing_type: str = ""
    security_deposit: int = 0
    bhk_type: str = ""
    area: int = 0
    registration_date: str = ""
    furniture_and_appliances: List[Dict[str, str]] = field(default_factory=list)
    amenities: List[str] = field(default_factory=list)
    user_id: str = ""

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
        
    def set_agreement_details(self, request):
        """
        Sets only the required agreement details from the request object.
        """
        fields_to_set = [
            "property_address",
            "city",
            "rent_amount",
            "agreement_period",
            "owner_address",
            "furnishing_type",
            "security_deposit",
            "bhk_type",
            "area",
            "registration_date",
            "furniture_and_appliances",
            "amenities",
            "user_id",
        ]

        for field in fields_to_set:
            if hasattr(request, field):
                setattr(self, field, getattr(request, field))

        # Handle tenant_details explicitly
        if hasattr(request, "tenant_details") and isinstance(request.tenant_details, list):
            if all(isinstance(tenant, dict) for tenant in request.tenant_details):
                self.tenant_details = request.tenant_details
            else:
                raise ValueError("tenant_details must be a list of dictionaries.")

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
