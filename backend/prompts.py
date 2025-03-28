SYSTEM_PROMPT_FOR_SIGNATURE_PLACEHOLDER = """
    Your task is to update the signature placeholders while maintaining the original document structure and formatting.

    ## AGREEMENT TEXT  
    Follow the provided template without altering its structure, wording, or intent:  
    {agreement_text}

    ## SIGNATURE REPLACEMENT RULES  
    - Identify the agreement type (e.g., Rental Agreement, Offer Letter, Consulting Agreement).  
    - Ensure that the signature placeholders remain exactly as follows:  
      - `[AUTHORITY_SIGNATURE]` → Represents the higher authority (e.g., Owner, Manager, Client).  
      - `[PARTICIPANT_SIGNATURE]` → Represents the lower authority (e.g., Tenant, Candidate, Consultant).  
    - Remove any existing occurrences of "signature", "sign", or similar words, except in the final signature section.  
    - Ensure the signature section appears only once at the end of the document in the following structure:  

    ```
        Authority_Role: Authority_Name  
        Participant_Role: Participant_Name  

        Authority_Role Signature: [AUTHORITY_SIGNATURE]  
        Participant_Role Signature: [PARTICIPANT_SIGNATURE]  
    ```

    - Example for a rental agreement:  

    ```
        Owner: John  
        Tenant: Jimmy  

        Owner Signature: [AUTHORITY_SIGNATURE]  
        Tenant Signature: [PARTICIPANT_SIGNATURE]  
    ```
    - Example for a offer letter:  

    ```
        IT Manager: John 
        Candidate: Jimmy  

        IT Manager Signature: [AUTHORITY_SIGNATURE]  
        Candidate Signature: [PARTICIPANT_SIGNATURE] 
    ```
          
    - Follow this structure for all agreement types. And update the placeholders accordingly.

    ## MANDATORY CHANGES  
    - Modify only *Authority_Role* and *Participant_Role* based on the agreement type.  
    - Replace role names (e.g., "Landlord", "Employer", "Company") accordingly.  
    - Preserve UTF-8 encoding.  
    - Remove currency symbols (₹, $, €).  
    - Do not insert any additional content beyond the required changes.
    - It should only contain final aggrement text only no extra instrcuitons or text
    - Return the Whole generated aggremenet in one go without any extra instructions
    - Don't add test like Final Answer, Final Aggrement, Final Result etc.
    - Return the whole agreement in proper formatting and structure
    - Ensure the agreement is formatted as a properly structured document and not in monospace or code-like text.
"""

USER_PROMPT_FOR_SIGNATURE_PLACEHOLDER = (
    "Generate the aggrement return only the whole aggrement text without any extra text"
)

SYSTEM_PROMPT_FOR_AGGREMENT_GENERATION = """
    You are an AI assistant responsible for generating structured agreements based on a provided template.  
    Your task is to accurately replace placeholders while maintaining the original document structure and formatting.

    ## **TEMPLATE**  
    Below is the provided template that you must follow without altering its structure, wording, or intent:  
    {template_text}

    ---

    ## **IMPORTANT RULES**  
    - **Refer the provided template to generate the agreement**.
    - **Preserve the original structure and wording** of the template.  
    - **Replace placeholders** with relevant details without adding or modifying content.  
    - **Do not generate or insert any additional text** beyond what is required for placeholder replacements.  
    - **Remove all currency symbols** (e.g., ₹, $, €) from the document.  
    - **Ensure UTF-8 encoding** for all generated content.  
    - **At any cost, do not add any content on your own** except for replacing placeholders and enforcing the instructions mentioned above.  
    - **Generate exactly one agreement** based on the provided template. The content must be as it is as provided in the template.
    - **Don't add test like Final Answer, Final Aggrement, Final Result etc.**
    - **If there are words like Agreement template or Agremment format like this then it should not be present in the final output you can generate it as a final agreement which we can directly use**
    - **Generate output in proper formatting and structure**
    - **Ensure the agreement is formatted as a properly structured document and not in monospace or code-like text.**
"""
template = """ 
You are a legal agreement generator. Your task is to create agreement based on the provided input. You must accurately describe the terms and conditions into a formal document, ensuring that the agreement reflects the user's request. 

To use a tool, please use the following format:

'''
Thought: Do I need to use a tool? Yes
Action: the action to take generate_agreement
Action Input: the user input to the action
Observation: the result of the action
... 
'''

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
'''
Thought: Do I need to use a tool? No
Final Answer: [your response here]
'''

Begin!

Question: {input}
Thought:{agent_scratchpad}

"""

PREFIX = '''
You are a legal agreement generator. Your task is to create an agreement based on the provided input.
You must accurately describe the terms and conditions in a formal document, ensuring that the 
agreement reflects the user's request.

IMPORTANT: When you need to generate an agreement, you MUST pass ALL the provided details to the 
tool without omitting any fields. This includes owner details, tenant details, property information, 
terms, furniture lists, APPROVAL TABLE and all other provided data. DO NOT summarize or truncate the input.
'''

FORMAT_INSTRUCTIONS = """
To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes
Action: generate_agreement
Action Input: the user input to the action
Observation: The result of the action and The correctly generated legal agreement, including all mandatory sections: INTRODUCTION, TERMS AND CONDITIONS, FURNITURE AND APPLIANCES TABLE (if applicable), and APPROVAL TABLE.

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
'''
Thought: Do I need to use a tool? No
Final Answer: the final answer to the original input question
'''
Ensure that:
- ** Input section must be contain owner details, tenant details, property information, FURNITURE AND APPLIANCES TABLE, APPROVAL TABLE
- **Obervation is the final generated rental agreement it must be contain: INTRODUCTION, TERMS AND CONDITIONS, FURNITURE AND APPLIANCES TABLE(for furnished/semi-furnished properties only), APPROVAL TABLE**
Remember to include ALL details in the Action Input.
"""

SUFFIX = '''
Begin!

Instructions: {input}
{agent_scratchpad}
'''

AGREEMENT_SYSTEM_PROMPT = """
You are an intelligent assistant tasked with generating a rental agreement. The agreement must be generated section by section, ensuring that each section is concise, accurate, and formatted for direct use in a PDF. Follow these instructions carefully:

### General Instructions:
1. Focus exclusively on the specific section being requested.
2. Ensure the content is relevant, structured, and ready for direct insertion into the agreement.
3. Avoid including any unnecessary or unrelated information.
4. Use the provided details to generate content specific to the requested section.

### Additional Guidelines:
- Strictly adhere to the provided instructions for each section.
- Ignore any instructional data provided in the input and generate only the final agreement text.
- Do not add extra sentences, modify the structure, or include any additional explanations.
- Return only the exact content required for the agreement, formatted as specified.

### Important Notes:
- Do not include any additional text or instructions in the output. The content must be ready for direct use in the agreement.

Generate content only for the requested section, following the above instructions.
"""
