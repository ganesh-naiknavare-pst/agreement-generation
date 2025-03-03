import asyncio
from datetime import datetime
import websockets
import json
import os
from helpers.state_manager import agreement_state
from config import WEBSOCKET_URL

class ApprovalTimeoutError(Exception):
    pass


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
                    print(f"Received approval response: {data}")

                    user_id = data.get("user_id")

                    if user_id in agreement_state.tenants:
                        agreement_state.tenants[user_id] = data.get("approved", False)
                        if agreement_state.tenants[user_id]:
                            tenant_name = agreement_state.tenant_names[user_id]
                            tenant_signature_path = agreement_state.tenant_signatures[user_id]
                            if os.path.isfile(tenant_signature_path):
                                agreement_state.tenant_signatures[user_id] = tenant_signature_path
                            else:
                                agreement_state.tenant_signatures[user_id] = (f"APPROVED BY {tenant_name} - {datetime.now()}" )

                            tenant_photo_path = ""
                            if os.path.isfile(tenant_photo_path):
                                agreement_state.tenant_photos[user_id] = tenant_photo_path
                            else:
                                agreement_state.tenant_photos[user_id] = (f"{tenant_name}" )
                        else:
                            print(f"Tenant {user_id} has rejected!")
                            return False

                    elif user_id == agreement_state.owner_id:
                        agreement_state.owner_approved = data.get("approved", False)
                        if agreement_state.owner_approved:
                            owner_signature_path = agreement_state.owner_signature
                            if os.path.exists(owner_signature_path):
                                agreement_state.owner_signature = owner_signature_path
                            else:
                                agreement_state.owner_signature = (
                                    f"APPROVED BY {agreement_state.owner_name} - {datetime.now()}"
                                )

                            owner_photo_path = ""
                            if os.path.exists(owner_photo_path):
                                agreement_state.owner_photo = owner_photo_path
                            else:
                                agreement_state.owner_photo = (f"{agreement_state.owner_name}")
                        else:
                            print("Owner has rejected!")
                            return False
                    # Check if both parties have responded
                    if agreement_state.is_fully_approved():
                        print("Both parties have approved!")
                        return True

                except asyncio.TimeoutError:
                    raise ApprovalTimeoutError(
                        f"Approval process timed out after {timeout_seconds} seconds"
                    )
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON received: {e}")
                    continue
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed unexpectedly")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket error: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False
