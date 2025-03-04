import asyncio
from datetime import datetime
import websockets
import json
import os
import logging
from helpers.state_manager import agreement_state
from config import WEBSOCKET_URL


class ApprovalTimeoutError(Exception):
    pass


# Configure logging
logging.basicConfig(level=logging.INFO)


async def listen_for_approval(timeout_seconds: int = 300) -> bool:
    """
    Listen for approval messages with a timeout.
    Args:
        timeout_seconds: Maximum time to wait for approvals (default 5 minutes)
    Returns:
        bool: True if both parties approved, False if rejected or timeout
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

                    if user_id in agreement_state.tenants:
                        agreement_state.tenants[user_id] = data.get("approved", False)
                        if agreement_state.tenants[user_id]:
                            tenant_name = agreement_state.tenant_names[user_id]
                            logging.info(
                                f"Tenant {tenant_name} ({user_id}) has approved the agreement."
                            )
                            tenant_signature_path = ""
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
                            return False

                    elif user_id == agreement_state.owner_id:
                        agreement_state.owner_approved = data.get("approved", False)
                        if agreement_state.owner_approved:
                            logging.info(
                                f"Owner {agreement_state.owner_name} ({user_id}) has approved the agreement."
                            )
                            owner_signature_path = ""
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
                            return False

                    # Check if both parties have responded
                    if agreement_state.is_fully_approved():
                        logging.info(
                            "Agreement successfully approved by Owner and Tenants."
                        )
                        return True

                except asyncio.TimeoutError:
                    raise ApprovalTimeoutError(
                        f"Approval process timed out after {timeout_seconds} seconds"
                    )
                except json.JSONDecodeError as e:
                    logging.error(f"Invalid JSON received: {e}")
                    continue
    except websockets.exceptions.ConnectionClosed:
        logging.error("WebSocket connection closed unexpectedly")
        return False
    except websockets.exceptions.WebSocketException as e:
        logging.error(f"WebSocket error: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return False
