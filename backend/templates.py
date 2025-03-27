from config import BASE_APPROVAL_URL, CORS_ALLOWED_ORIGIN
from helpers.state_manager import agreement_state, template_agreement_state
from datetime import datetime

REJECTION_NOTIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agreement Rejected</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center;">
    <table role="presentation" width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td align="center" style="padding: 20px;">
                <table role="presentation" width="600" bgcolor="#ffffff" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td bgcolor="#dc3545" style="padding: 15px; font-size: 20px; font-weight: bold; color: #ffffff; text-align: center; border-radius: 8px 8px 0 0;">
                            Agreement Rejected
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 20px; font-size: 16px; color: #333333; text-align: left; line-height: 1.5;">
                            <p>Hello,</p>
                            <p>{message}</p>
                            <p>If you have any questions or need to generate a new agreement, please contact the property owner.</p>
                            <p>Best regards,</p>
                            <p><strong>Agreement Agent Team</strong></p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 15px; font-size: 14px; color: #666666; text-align: center; border-top: 1px solid #dddddd;">
                            This email was generated automatically as part of the agreement process. Please do not respond to this email.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>

"""

FULLY_APPROVED_TEMPLATE = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agreement Fully Approved</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center;">
        <table role="presentation" width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td align="center" style="padding: 20px;">
                    <table role="presentation" width="600" bgcolor="#ffffff" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">

                        <!-- Header -->
                        <tr>
                            <td bgcolor="#28a745" style="padding: 15px; font-size: 20px; font-weight: bold; color: #ffffff; text-align: center; border-radius: 8px 8px 0 0;">
                                Agreement Fully Approved
                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td style="padding: 20px; font-size: 16px; color: #333333; text-align: left; line-height: 1.5;">
                                <p>Hello,</p>
                                <p>{message}</p>
                                <p>Please find the signed agreement attached for your reference.</p>
                                <p>Best regards,</p>
                                <p><strong>Agreement Agent Team</strong></p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding: 15px; font-size: 14px; color: #666666; text-align: center; border-top: 1px solid #dddddd;">
                                This email was generated automatically as part of the agreement process. Please do not respond to this email.
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
"""


PENDING_APPROVAL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agreement for {role}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center;">

    <table role="presentation" width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td align="center" style="padding: 20px;">
                <table role="presentation" width="600" bgcolor="#ffffff" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">

                    <!-- Header -->
                    <tr>
                        <td bgcolor="#007bff" style="padding: 15px; font-size: 20px; font-weight: bold; color: #ffffff; text-align: center; border-radius: 8px 8px 0 0;">
                            Agreement for {role}
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 20px; font-size: 16px; color: #333333; text-align: left; line-height: 1.5;">
                            <p>Hello,</p>
                            <p>Please proceed with the agreement.</p>
                            <p>To proceed, please verify your identity by uploading your signature and photo.</p>
                            <p>After uploading your signature and photo, you will be able to approve or reject the agreement.</p>
                            
                            <!-- Review Agreement Button -->
                            <table role="presentation" align="center" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td align="center" style="padding: 10px;">
                                        <a href="{url}" style="background-color: #228be6; color: #ffffff; padding: 12px 20px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 16px;">
                                            Click to Proceed
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <p>Best regards,</p>
                            <p><strong>Agreement Agent Team</strong></p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 15px; font-size: 14px; color: #666666; text-align: center; border-top: 1px solid #dddddd;">
                            This email was generated automatically as part of the agreement process. Please do not respond to this email.
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>

</body>
</html>
"""


def generate_email_template(
    role: str,
    user_id: str,
    agreement_id: int,
    is_template: bool = False,
    is_rejection: bool = False,
    rejected_by: str = None,
) -> str:

    agreement_type_str = "template" if is_template else "rent"
    url = f"{CORS_ALLOWED_ORIGIN}/review-agreement/{user_id}/{agreement_id}?type={agreement_type_str}"
    if is_rejection:
        message = f"The agreement has been rejected by {rejected_by}."
        return REJECTION_NOTIFICATION_TEMPLATE.format(message=message)
    elif (
        agreement_state.is_fully_approved()
        or template_agreement_state.is_fully_approved()
    ):
        message = (
            "The agreement has been approved"
            if is_template
            else "The rental agreement has been approved"
        )
        return FULLY_APPROVED_TEMPLATE.format(message=message)

    else:
        agreement_type = "agreement" if is_template else "rental agreement"
        return PENDING_APPROVAL_TEMPLATE.format(
            role=role,
            agreement_type=agreement_type,
            url=url,
        )


def parse_datetime(date_str: str) -> datetime:
    formats = ["%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Date string '{date_str}' does not match expected formats.")

def format_agreement_details(
    owner_name: str,
    tenant_details: list,
    property_address: str,
    city: str,
    rent_amount: int,
    agreement_period: list,
) -> str:
    start_date, end_date = agreement_period
    start_date_obj = parse_datetime(start_date)
    end_date_obj = parse_datetime(end_date)
    num_months = (
        (end_date_obj.year - start_date_obj.year) * 12
        + end_date_obj.month
        - start_date_obj.month
    )
    return f"""
Create a rental agreement with the following details:

Owner: {owner_name}

Tenants:
{chr(10).join(f'{i+1}. {t["name"]}' for i, t in enumerate(tenant_details))}

Property Details:
- Address: {property_address}
- City: {city}
- Monthly Rent: Rs. {rent_amount}
- Duration: {num_months} months (From {start_date} to {end_date})

Additional Terms:
- Rent will be split equally among all tenants
- Each tenant is jointly and severally liable for the full rent amount
- All tenants must agree to any changes in the agreement
- Security deposit will be Rs. {rent_amount} (collected equally from each tenant)
"""
