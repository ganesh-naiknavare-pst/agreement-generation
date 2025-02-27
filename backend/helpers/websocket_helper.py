import asyncio
from datetime import datetime
import websockets
import json
from helpers.state_manager import agreement_state, template_agreement_state
from config import WEBSOCKET_URL

class ApprovalTimeoutError(Exception):
    pass


async def listen_for_approval(timeout_seconds: int = 300, is_template: bool=False) -> bool:
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

                    if is_template:
                        if user_id == template_agreement_state.participent_id:
                            template_agreement_state.participent_approved = data.get("approved", False)
                            if template_agreement_state.participent_approved:
                                template_agreement_state.participent_signature = (f"APPROVED BY PARTICIPANT - {datetime.now()}")
                                print("Participant has approved!")
                            else:
                                print("Participant has rejected!")
                                return False

                        elif user_id == template_agreement_state.authority_id:
                            template_agreement_state.authority_approved = data.get("approved", False)
                            if template_agreement_state.authority_approved:
                                template_agreement_state.authority_signature = (f"APPROVED BY AUTHORITY - {datetime.now()}")
                                print("Authority has approved!")
                            else:
                                print("Authority has rejected!")
                                return False
                        
                    else:
                        if user_id in agreement_state.tenants:
                            agreement_state.tenants[user_id] = data.get("approved", False)
                            if agreement_state.tenants[user_id]:
                                tenant_name = agreement_state.tenant_names[user_id]
                                agreement_state.tenant_signatures[user_id] = (
                                    f"APPROVED BY {tenant_name} - {datetime.now()}"
                                )
                                print(f"Tenant {tenant_name} has approved!")
                            else:
                                print(f"Tenant {user_id} has rejected!")
                                return False

                        elif user_id == agreement_state.owner_id:
                            agreement_state.owner_approved = data.get("approved", False)
                            if agreement_state.owner_approved:
                                agreement_state.owner_signature = (
                                    f"APPROVED BY {agreement_state.owner_name} - {datetime.now()}"
                                )
                                print(f"Owner {agreement_state.owner_name} has approved!")
                            else:
                                print("Owner has rejected!")
                                return False
                    # Check if both parties have responded
                    if agreement_state.is_fully_approved() or template_agreement_state.is_fully_approved():
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
