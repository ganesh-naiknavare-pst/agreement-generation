from config import BASE_APPROVAL_URL, CORS_ALLOWED_ORIGIN
from helpers.state_manager import agreement_state, template_agreement_state
from datetime import datetime
from typing import List, Dict, Optional

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


def format_agreement_details(
    owner_name: str,
    tenant_details: list,
    property_address: str,
    city: str,
    rent_amount: int,
    agreement_period: list,
    owner_address: str,
    furnishing_type: str,
    security_deposit: int,
    bhk_type: str,
    area: int,
    registration_date: str,
    furniture_and_appliances: List[Dict[str, str]],
    amenities: List[str],
) -> str:
    start_date, end_date = agreement_period
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f%z")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%f%z")
    num_months = (
        (end_date_obj.year - start_date_obj.year) * 12
        + end_date_obj.month
        - start_date_obj.month
    )

    furniture_list = ", ".join(
        f"{item['name']}{'s' if int(item['units']) > 1 else 'Not provided any furniture'} {item['units']}"
        for item in furniture_and_appliances
    )

    amenities_list = (
        "\n".join(f"  - {amenity}" for amenity in amenities)
        if amenities
        else "No aminities"
    )
    furniture_table = (
        "\n".join(
            f"| {item['sr_no']}  | {item['name']} | {item['units']} |"
            for item in furniture_and_appliances
        )
        if furniture_and_appliances
        else "Not provided any furniture."
    )
    return f"""
RENTAL AGREEMENT REQUIREMENTS:

MANDATORY DATA- REQUIRED (MUST BE INCLUDED):
OWNER DETAILS:
    NAME: {owner_name}
    ADDRESS: {owner_address}
TENANTS DETAILS:
    Name: {chr(10).join(f'{i+1}. {t["name"]}' for i, t in enumerate(tenant_details))}
    Address: {chr(10).join(f'{i+1}. {t["address"]}' for i, t in enumerate(tenant_details))}
TERMS: Rs. {rent_amount}/month, {num_months} months ({start_date} to {end_date})
DEPOSIT: Rs. {security_deposit}
REGISTERED DATE: {registration_date}
PROPERTY DETAILS: Address: {property_address}, City: {city}, bhk type {bhk_type}, Area: {area} sq. ft., furnishing_type: {furnishing_type}

IMPORTANT: The agreement MUST begin with a proper INTRODUCTION section that includes ALL the above mandatory data fields in agreements. This section must clearly state all owner details, tenant details, rental terms, deposit amount, registration date, and complete property details.

REQUIRED SECTIONS - MUST INCLUDE 2-4 DETAILED POINTS FOR EACH,  MINIMUM 3O to 50 WORDS PER SENTANCE:
TERMS AND CONDITIONS:
1. LICENSE FEE: MUST cover payment of Rs. {rent_amount}, due dates, escalation
2. DEPOSIT: MUST specify Rs. {security_deposit} amount, refund process, deductions, timeline
3. FURNITURE AND APPLIANCES: Tenants shall maintain all items in good condition  and MUST explain complete furniture list {furniture_list},damage reporting procedure, replacement responsibility
4. UTILITIES: MUST detail all bill responsibilities, payment methods, connections, shared costs
5. TENANT DUTIES: MUST list maintenance requirements, prohibitions, cleanliness, occupancy
6. OWNER RIGHTS: MUST outline inspection protocols, notice periods, access conditions, showings
7. TERMINATION: MUST define notice periods, early exit penalties, inspection process, deposit rules
8. ALTERATIONS: MUST prohibit unauthorized changes, permission process, restoration, fixtures
9. AMENITIES: MUST describe access to {amenities_list}, usage rules, restrictions, maintenance

### FURNITURE AND APPLIANCES TABLE - REQUIRED (MUST BE INCLUDED):
   * The premises contain the following **furniture and appliances** provided by the owner. Tenants shall maintain all items in good condition and will be responsible for any **damages beyond normal wear and tear**.  
    | Sr. No | Item                 | Count  |
    |--------|----------------------|--------|
    {furniture_table}

### APPROVAL TABLE - REQUIRED (MUST BE THE FINAL SECTION):
Note: The table MUST follow this PRECISE structure WITHOUT ANY MODIFICATIONS:
PARTIAL TABLES ARE STRICTLY PROHIBITED – every row for the Owner and ALL Tenants must be fully present dont add extra or miss the filed.

| Name and Address               | Photo           | Signature           |  
|--------------------------------|-----------------|---------------------|  
| **Owner:**                     |                 |                     |  
| **Name:** {owner_name}         | [OWNER PHOTO]   | [OWNER SIGNATURE]   |  
| **Address:** {owner_address}   |                 |                     |  
|--------------------------------|-----------------|---------------------|  
| **Tenant 1:**                  |                 |                     |  
| **Name:** [TENANT 1 NAME]      | [TENANT 1 PHOTO]| [TENANT 1 SIGNATURE]|  
| **Address:** [TENANT 1 ADDRESS]|                 |                     |  
|--------------------------------|-----------------|---------------------|
CRITICAL: 
- STRICTLY PROHIBITED to generate partial, incomplete rental agreements or tables with missing fields
- Replace [TENANT n NAME] and [TENANT n ADDRESS] with real data for all tenants
- BOTH FURNITURE TABLE AND APPROVAL TABLE MUST BE INCLUDED IN EVERY AGREEMENT AND THE APPROVAL TABLE MUST ALWAYS BE THE FINAL SECTION OF THE AGREEMENT.
- If a furniture list is provided, then generate the  FURNITURE AND APPLIANCES section and FURNITURE AND APPLIANCES TABLE otherwise, return "No furniture provided."
- STRICTLY number tenants as TENANT 1, TENANT 2, etc. - NO variations permitted
- FURNITURE AND APPLIANCES section and FURNITURE AND APPLIANCES TABLE must be COMPLETELY SEPARATE SECTIONS - DO NOT merge them together or place the table within section 
- PARTIAL TABLES ARE STRICTLY PROHIBITED – every row for the Owner and ALL Tenants must be fully present and for tenants must be replace with real time data for name and address.

"""
