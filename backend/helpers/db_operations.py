from prisma.enums import AgreementStatus
from api.routes.websocket import notify_clients
from prisma import Base64

async def update_agreement_status(db, agreement_id: int, status: AgreementStatus, is_template: bool = False):
    """Updates the agreement status in the database."""
    # Determine the appropriate table based on is_template
    table = db.templateagreement if is_template else db.agreement
    await table.update(where={"id": agreement_id}, data={"status": status})


async def create_user_agreement_status(db, user_id: int, agreement_id: int, status: AgreementStatus, is_template: bool = False):
    """Creates a user agreement status entry if it does not exist."""
    # Determine the appropriate table based on is_template
    table = db.useragreementstatus if is_template else db.userrentagreementstatus

    # Store the user agreement status in the database
    existing_user = await table.find_first(
        where={"userId": user_id, "agreementId": agreement_id}
    )
    if not existing_user:
        await table.create(
            data={"userId": user_id, "agreementId": agreement_id, "status": status}
        )
        await notify_clients({"userId": user_id, "status": status})

async def store_final_pdf(db, agreement_id: int, pdf_path: str):
    """Encodes the final PDF and stores it in the database."""
    with open(pdf_path, "rb") as pdf_file:
        pdf_base64 = Base64.encode(pdf_file.read())

    await db.agreement.update(
        where={"id": agreement_id},
        data={"pdf": pdf_base64, "status": AgreementStatus.APPROVED},
    )
