from config import  BASE_APPROVAL_URL
from helpers.state_manager import agreement_state, template_agreement_state

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

FULLY_APPROVED_TEMPLATE="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agreement Rejected</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #dc3545;
            border-radius: 4px;
            color: #dc3545;
            background-color: #f8d7da;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="alert">
            <p>Agreement Rejected</p>
        </div>
        <p>Hello,</p>
        <p>{message}</p>
        <p>For any questions or to generate a new agreement, please contact the property owner.</p>
        <p>Best regards,<br>Agreement Agent Team</p>
    </div>
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
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <p>Hello,</p>
        <p>{message}</p>
        <p>Please find the signed agreement attached for your reference.</p>
        <p>Best regards,<br>Agreement Agent Team</p>
    </div>
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
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 5px;
            border-radius: 5px;
            text-decoration: none;
            color: white;
        }}
        .approve {{
            background-color: #28a745;
        }}
        .reject {{
            background-color: #dc3545;
        }}
    </style>
</head>
<body>
    <div class="container">
        <p>Hello,</p>
        <p>Please review and sign the attached {agreement_type} document.</p>
        <p>Click on one of the following links to approve or reject the agreement:</p>
        <p>
            <a href="{approve_url}" class="button approve">Approve Agreement</a>
            <a href="{reject_url}" class="button reject">Reject Agreement</a>
        </p>
        <p>Best regards,<br>Agreement Agent Team</p>
    </div>
</body>
</html>
"""

def generate_email_template(role: str, user_id: str, is_template: bool=False, is_rejection: bool=False, rejected_by: str=None) -> str:
    
    approve_url = f"{BASE_APPROVAL_URL}/sign/{user_id}/approve"
    reject_url = f"{BASE_APPROVAL_URL}/sign/{user_id}/reject"

    if is_rejection:
        message = f"The agreement has been rejected by {rejected_by}."
        return REJECTION_NOTIFICATION_TEMPLATE.format(message=message)
    elif agreement_state.is_fully_approved() or template_agreement_state.is_fully_approved():
        message = "The agreement has been approved" if is_template else "The rental agreement has been approved"
        return FULLY_APPROVED_TEMPLATE.format(message=message)
    
    else:
        agreement_type = "agreement" if is_template else "rental agreement"
        return PENDING_APPROVAL_TEMPLATE.format(
            role=role,
            agreement_type=agreement_type,
            approve_url=approve_url,
            reject_url=reject_url
        )

def format_agreement_details(owner_name: str, tenant_details: list, property_address: str,
                           city: str, rent_amount: str, start_date: str) -> str:
    return f"""
Create a rental agreement with the following details:

Owner: {owner_name}

Tenants:
{chr(10).join(f'{i+1}. {t["name"]}' for i, t in enumerate(tenant_details))}

Property Details:
- Address: {property_address}
- City: {city}
- Monthly Rent: Rs. {rent_amount}
- Agreement Start Date: {start_date}
- Duration: 11 months

Additional Terms:
- Rent will be split equally among all tenants
- Each tenant is jointly and severally liable for the full rent amount
- All tenants must agree to any changes in the agreement
- Security deposit will be Rs. {rent_amount} (collected equally from each tenant)
"""
