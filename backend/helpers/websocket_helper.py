import asyncio
from datetime import datetime
import websockets
import json
import os
import logging
from helpers.state_manager import agreement_state, template_agreement_state
from config import WEBSOCKET_URL
from enum import Enum


class ApprovalTimeoutError(Exception):
    pass


class ConnectionClosedError(Exception):
    pass


class ApprovalResult(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    CONNECTION_CLOSED = "connection_closed"


# Configure logging
logging.basicConfig(level=logging.INFO)

async def listen_for_approval(timeout_seconds: int = 300, is_template: bool=False) -> ApprovalResult:
    """
    Listen for approval messages with a timeout.
    Args:
        timeout_seconds: Maximum time to wait for approvals (default 5 minutes)
    Returns:
        ApprovalResult: APPROVED if all parties approved, REJECTED if explicitly rejected,
                       CONNECTION_CLOSED if connection issues occurred
    Raises:
        ApprovalTimeoutError: If no response received within timeout period
    """
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            while True:
                try:
                    # Set timeout for receiving messages
                    response = await asyncio.wait_for(
                        websocket.recv(), timeout=timeout_seconds
                    )
                    data = json.loads(response)
                    logging.info(f"Received approval response: {data}")

                    user_id = data.get("user_id")

                    if is_template:
                        if user_id == template_agreement_state.participant_id:
                            template_agreement_state.participant_approved = data.get("approved", False)
                            if template_agreement_state.participant_approved:
                                participant_signature_path = template_agreement_state.participant_signature
                                if os.path.isfile(participant_signature_path):
                                    template_agreement_state.participant_signature = participant_signature_path
                                else:
                                    template_agreement_state.participant_signature = (f"APPROVED BY PARTICIPANT - {datetime.now()}")
                                print("Participant has approved!")
                            else:
                                print("Participant has rejected!")
                                return ApprovalResult.REJECTED

                        elif user_id == template_agreement_state.authority_id:
                            template_agreement_state.authority_approved = data.get("approved", False)
                            if template_agreement_state.authority_approved:
                                authority_signature_path = template_agreement_state.authority_signature
                                if os.path.isfile(authority_signature_path):
                                    template_agreement_state.authority_signature = authority_signature_path
                                else:
                                    template_agreement_state.authority_signature = (f"APPROVED BY AUTHORITY - {datetime.now()}")
                                print("Authority has approved!")
                            else:
                                print("Authority has rejected!")
                                return ApprovalResult.REJECTED                     
                    else:
                        if user_id in agreement_state.tenants:
                            agreement_state.tenants[user_id] = data.get("approved", False)
                            if agreement_state.tenants[user_id]:
                                tenant_name = agreement_state.tenant_names[user_id]
                                logging.info(
                                    f"Tenant {tenant_name} ({user_id}) has approved the agreement."
                                )
                                tenant_signature_path = agreement_state.tenant_signatures[user_id]
                                if os.path.isfile(tenant_signature_path):
                                    agreement_state.tenant_signatures[user_id] = (
                                        tenant_signature_path
                                    )
                                else:
                                    agreement_state.tenant_signatures[user_id] = (
                                        f"APPROVED BY {tenant_name} - {datetime.now()}"
                                    )

                                tenant_photo_path = agreement_state.tenant_photos[user_id]
                                if os.path.isfile(tenant_photo_path):
                                    agreement_state.tenant_photos[user_id] = (
                                        tenant_photo_path
                                    )
                                else:
                                    agreement_state.tenant_photos[user_id] = (
                                        f"{tenant_name}"
                                    )
                            else:
                                logging.warning(f"Tenant {user_id} has rejected!")
                                return ApprovalResult.REJECTED

                        elif user_id == agreement_state.owner_id:
                            agreement_state.owner_approved = data.get("approved", False)
                            if agreement_state.owner_approved:
                                logging.info(
                                    f"Owner {agreement_state.owner_name} ({user_id}) has approved the agreement."
                                )
                                owner_signature_path = agreement_state.owner_signature
                                if os.path.exists(owner_signature_path):
                                    agreement_state.owner_signature = owner_signature_path
                                else:
                                    agreement_state.owner_signature = f"APPROVED BY {agreement_state.owner_name} - {datetime.now()}"

                                owner_photo_path = agreement_state.owner_photo
                                if os.path.exists(owner_photo_path):
                                    agreement_state.owner_photo = owner_photo_path
                                else:
                                    agreement_state.owner_photo = (
                                        f"{agreement_state.owner_name}"
                                    )
                            else:
                                logging.warning("Owner has rejected!")
                                return ApprovalResult.REJECTED

                    # Check if both parties have responded
                    if agreement_state.is_fully_approved() or template_agreement_state.is_fully_approved():
                        message = (
                            "Agreement successfully approved by Authority and Participant."
                            if template_agreement_state.is_fully_approved()
                            else "Agreement successfully approved by Owner and Tenants."
                        )
                        logging.info(message)
                        return ApprovalResult.APPROVED

                except asyncio.TimeoutError:
                    logging.error("Approval process timed out")
                    return ApprovalResult.CONNECTION_CLOSED
                except json.JSONDecodeError as e:
                    logging.error(f"Invalid JSON received: {e}")
                    continue
    except websockets.exceptions.ConnectionClosed:
        logging.error("WebSocket connection closed unexpectedly")
        return ApprovalResult.CONNECTION_CLOSED
    except websockets.exceptions.WebSocketException as e:
        logging.error(f"WebSocket error: {str(e)}")
        return ApprovalResult.CONNECTION_CLOSED
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return ApprovalResult.CONNECTION_CLOSED

