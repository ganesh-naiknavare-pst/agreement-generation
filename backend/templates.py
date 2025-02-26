def generate_email_template(role: str, user_id: str, base_approval_url: str) -> str:
    approve_url = f"{base_approval_url}/{user_id}/approve"
    reject_url = f"{base_approval_url}/{user_id}/reject"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rental Agreement for {role}</title>
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
            <p>Please review and sign the attached rental agreement document.</p>
            <p>Click on one of the following links to approve or reject the agreement:</p>
            <p>
                <a href="{approve_url}" class="button approve">Approve Agreement</a>
                <a href="{reject_url}" class="button reject">Reject Agreement</a>
            </p>
            <p>Best regards,<br>Docu Sign Team</p>
        </div>
    </body>
    </html>
    """

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
