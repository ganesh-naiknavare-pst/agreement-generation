from config import BASE_APPROVAL_URL, CORS_ALLOWED_ORIGIN
from helpers.state_manager import state_manager
from datetime import datetime
from typing import List, Dict, Optional
import logging

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
    if is_template:
        current_state = state_manager.get_template_agreement_state(agreement_id)
    else:
        current_state = state_manager.get_agreement_state(agreement_id)

    if current_state is None:
        logging.error("No active agreement state found")
        return

    agreement_type_str = "template" if is_template else "rent"

    url = f"{CORS_ALLOWED_ORIGIN}/review-agreement/{user_id}/{agreement_id}?type={agreement_type_str}"
    print(f"URL---> {url}")

    if is_rejection:
        message = f"The agreement has been rejected by {rejected_by}."
        return REJECTION_NOTIFICATION_TEMPLATE.format(message=message)
    elif current_state.is_fully_approved():
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
    start_date_obj = parse_datetime(start_date)
    end_date_obj = parse_datetime(end_date)
    num_months = (
        (end_date_obj.year - start_date_obj.year) * 12
        + end_date_obj.month
        - start_date_obj.month
    )

    furniture_list = ", ".join(
        f"{item['name']} ({item['units']} units)" for item in furniture_and_appliances
    ) if furniture_and_appliances else "No furniture provided."

    amenities_list = ", ".join(amenities) if amenities else "No amenities provided."

    tenants_info = "\n".join(
        f"{i+1}. Name: {t['name']}, Address: {t['address']}" for i, t in enumerate(tenant_details)
    )

    tenants_approval = "\n".join(
        f"    {i+1}. Name: {t['name']}, Address: {t['address']}" for i, t in enumerate(tenant_details)
    )

    return f"""
RENTAL AGREEMENT DETAILS

INTRODUCTION:
    Owner Name: {owner_name}
    Owner Address: {owner_address}
    Tenants:
{tenants_info}
    Property Address: {property_address}, City: {city}
    BHK Type: {bhk_type}, Area: {area} sq. ft.
    Furnishing Type: {furnishing_type}
    Rent Amount: Rs. {rent_amount}/month
    Duration: {num_months} months ({start_date} to {end_date})
    Security Deposit: Rs. {security_deposit}
    Registration Date: {registration_date}

TERMS AND CONDITIONS:
    License Fee: Payment details including Rs. {rent_amount}, due dates, and escalation terms.
    Deposit: Refund process, deductions, and timelines for Rs. {security_deposit}.
    Utilities: Responsibilities for bill payments, shared costs, and connection setup.
    Tenant Duties: Maintenance requirements, prohibitions, cleanliness, and occupancy rules.
    Owner Rights: Inspection protocols, notice periods, and property access conditions.
    Termination: Notice periods, penalties for early exit, and deposit refund conditions.
    Alterations: Restrictions on modifications, approval process, and restoration requirements.
    Amenities: Access to facilities - {amenities_list}, including rules and maintenance.

FURNITURE AND APPLIANCES:
    Items provided: {furniture_list}
    Maintenance responsibility lies with tenants, covering damages beyond normal wear and tear.

APPROVAL SECTION:
    Owner Name: {owner_name}
    Owner Address: {owner_address}
    Tenants:
{tenants_approval}
    All parties must review and sign the agreement before proceeding.
"""

def generate_introduction_section(owner_name, owner_address, tenants, property_address, city, bhk_type, area, furnishing_type, rent_amount, agreement_period, security_deposit, registration_date):
    """Generates the Introduction & Basic Details section with strict formatting and validation."""
    
    print(f"Agreement Period: {agreement_period}")
    start_date, end_date = agreement_period
    print(f"Start Date: {start_date}, End Date: {end_date}")
    
    if isinstance(start_date, datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S%z")
    if isinstance(end_date, datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    start_date_obj = parse_datetime(start_date)
    end_date_obj = parse_datetime(end_date)
    
    num_months = (end_date_obj.year - start_date_obj.year) * 12 + (end_date_obj.month - start_date_obj.month)
    
    tenant_details = "\n".join(f"{i+1}. {t['name']}, Address: {t['address']}" for i, t in enumerate(tenants))

    data = f"""
    ### RENTAL AGREEMENT

    **REQUIRED SECTIONS - MUST INCLUDE ALL DETAILS AS SPECIFIED:**  
    - Add proper heading at the start of the section.
    - The agreement must contain complete and accurate **Owner Details, Tenant Details, Agreement Terms, and Property Details**.  
    - **Dates must be in the correct format (YYYY-MM-DDTHH:MM:SS±HHMM).**  
    - **No section should be omitted or modified.** Ensure all details are properly structured.  
    - The agreement period must be calculated in months and clearly specified.  

    **OWNER DETAILS:**  
    - **Name:** {owner_name}  
    - **Address:** {owner_address}  

    **TENANT DETAILS:**  
    {tenant_details}  

    **AGREEMENT TERMS:**  
    - **Rent:** Rs. {rent_amount}/month  
    - **Duration:** {num_months} months ({start_date} to {end_date})  
    - **Security Deposit:** Rs. {security_deposit}  
    - **Registration Date:** {registration_date}  

    **PROPERTY DETAILS:**  
    - **Address:** {property_address}  
    - **City:** {city}  
    - **BHK Type:** {bhk_type}  
    - **Area:** {area} sq. ft.  
    - **Furnishing Type:** {furnishing_type}  
    """

    return data

def generate_terms_conditions_section(rent_amount, security_deposit, amenities):
    """Generates the Terms & Conditions section with detailed instructions."""
    data = f"""
    **Add proper heading at the start of the section.**
    **Each section MUST include 1-2 detailed points, with a minimum of 30 to 50 words per section.**  
    ### TERMS & CONDITIONS

    1. **LICENSE FEE**: Must clearly define the payment of Rs. {rent_amount}, including due dates, escalation terms, and any applicable late fees.  
    2. **SECURITY DEPOSIT**: Must specify the amount (Rs. {security_deposit}), refund process, permissible deductions, and the expected timeline for returns.  
    3. **UTILITIES**: Must outline tenant responsibilities for electricity, water, gas, internet, and other utilities, including payment methods, shared costs, and connection details.  
    4. **TENANT RESPONSIBILITIES**: Must list maintenance obligations, restrictions on alterations, cleanliness expectations, and occupancy limits.  
    5. **OWNER RIGHTS**: Must describe inspection protocols, required notice periods for entry, conditions for access, and procedures for property showings.  
    6. **TERMINATION POLICY**: Must define notice periods for lease termination, early exit penalties, final inspection requirements, and security deposit refund rules.  
    7. **PROPERTY ALTERATIONS**: Must prohibit unauthorized modifications, define the approval process for changes, outline restoration responsibilities, and specify handling of fixtures.  
    8. **AMENITIES**: Must provide a clear description of available amenities ({', '.join(amenities)}), along with their usage rules, restrictions, and maintenance responsibilities.  
    """
    return data
