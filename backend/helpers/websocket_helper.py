import asyncio
from datetime import datetime
import websockets
import json
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

                    if data.get("user_id") == agreement_state.tenant_id:
                        agreement_state.tenant_approved = data.get("approved", False)
                        if agreement_state.tenant_approved:
                            agreement_state.tenant_signature = (
                                f"APPROVED BY TENANT - {datetime.now()}"
                            )
                            print("Tenant has approved!")
                        else:
                            print("Tenant has rejected!")
                            return False

                    elif data.get("user_id") == agreement_state.owner_id:
                        agreement_state.owner_approved = data.get("approved", False)
                        if agreement_state.owner_approved:
                            agreement_state.owner_signature = (
                                f"APPROVED BY OWNER - {datetime.now()}"
                            )
                            print("Owner has approved!")
                        else:
                            print("Owner has rejected!")
                            return False

                    # Check if both parties have responded
                    if agreement_state.is_fully_approved():
                        print("Both parties have approved!")
                        return True

                except asyncio.TimeoutError:
                    raise ApprovalTimeoutError(
                        "Approval process timed out after " f"{timeout_seconds} seconds"
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
