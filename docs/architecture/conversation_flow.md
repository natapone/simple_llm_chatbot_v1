# Conversation Flow Design

This document outlines the conversation flow design for the pre-sales assistant chatbot.

## Conversation States

The chatbot conversation follows a state-based approach, with each state representing a different phase of the conversation:

```
┌─────────────────┐
│                 │
│     Greeting    │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Requirement   │
│    Gathering    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Use Case     │
│  Understanding  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Timeline &    │
│   Expectations  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Budget      │
│     Inquiry     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Summarization  │
│ & Confirmation  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Contact     │
│   Collection    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Handoff     │
│                 │
└─────────────────┘
```

## State Descriptions

### 1. Greeting & Context Setting

**Purpose**: Establish rapport and understand the initial request.

**Example Prompt**:
```
Hello! I'm here to understand your software development needs. How can I assist you today?
```

**Expected User Responses**:
- "I want a mobile app."
- "We need a CRM system."
- "I need a chatbot for customer service."

**Transition Logic**:
- If user provides project type → Requirement Gathering
- If user asks about capabilities → Provide information and return to Greeting
- If user provides detailed requirements → Skip to Use Case Understanding

### 2. Requirement Gathering

**Purpose**: Collect specific requirements and features.

**Example Prompt**:
```
That sounds interesting! Could you describe the key features or functionalities you have in mind?
```

**Expected User Responses**:
- "A mobile app with payment integration."
- "A chatbot that can handle customer FAQs."
- "An inventory management system."

**Transition Logic**:
- After collecting requirements → Use Case Understanding
- If requirements are vague → Ask clarifying questions and remain in Requirement Gathering

### 3. Use Case Understanding

**Purpose**: Understand the context and purpose of the project.

**Example Prompt**:
```
Got it! Is this solution for internal use or customer-facing?
```

**Expected User Responses**:
- "Internal for our employees."
- "For our customers to use."

**Transition Logic**:
- After understanding use case → Timeline & Expectations
- If use case is complex → Ask follow-up questions and remain in Use Case Understanding

### 4. Timeline & Expectations Inquiry

**Purpose**: Determine project timeline and scope expectations.

**Example Prompt**:
```
What's your expected timeline for this project? Are you looking for a prototype first or a full solution?
```

**Expected User Responses**:
- "We need a prototype in 2 months."
- "A full solution in 6 months."

**Transition Logic**:
- After collecting timeline information → Budget Inquiry
- If timeline is unrealistic → Provide feedback and ask for reconsideration

### 5. Budget Inquiry (Indirect Approach)

**Purpose**: Tactfully gather budget information.

**Example Prompt**:
```
Would you like recommendations based on different pricing options, or do you already have a budget range in mind?
```

**Expected User Responses**:
- "We have a budget but would like to explore options."
- "We want to stay within $10,000-$20,000."

**Transition Logic**:
- After budget discussion → Summarization & Confirmation
- If user is hesitant about budget → Skip to Summarization & Confirmation

### 6. Summarization & Confirmation

**Purpose**: Verify collected information and ensure accuracy.

**Example Prompt**:
```
To summarize, you need a [solution] for [use case], with key features like [features]. You prefer [timeline] and are open to budget discussions. Is this correct?
```

**Expected User Responses**:
- "Yes, that sounds right."
- "No, I also need [additional feature]."

**Transition Logic**:
- If confirmation is positive → Contact Collection
- If correction is needed → Update information and repeat Summarization

### 7. Contact Collection

**Purpose**: Gather contact information for follow-up.

**Example Prompt**:
```
Could you share your email or phone number so we can follow up with recommendations?
```

**Expected User Responses**:
- "[email@example.com]"
- "You can reach me at [phone number]."

**Transition Logic**:
- After collecting contact information → Lead Storage
- If user is hesitant → Explain purpose and privacy policy

### 8. Lead Storage

After collecting all necessary information, the chatbot will:

- Compile all collected information into a structured format
- Store all collected information in CSV storage
- Confirm to the user that their information has been recorded
- Provide information about next steps (e.g., "Our team will contact you within 24 hours")

#### 7.1 Data Structure

The following information will be stored in the CSV file:

| Field | Description |
|-------|-------------|
| Timestamp | When the conversation occurred |
| Client Name | Full name of the potential client |
| Contact Information | Email and/or phone number |
| Project Type | Type of software project (web app, mobile app, etc.) |
| Requirements Summary | Brief summary of the client's requirements |
| Timeline | Expected timeline for the project |
| Budget Range | Approximate budget range for the project |
| Follow-up Status | Current status of the lead (New, Contacted, In Discussion, etc.) |
| Conversation Summary | Summary of the entire conversation |

#### 7.2 CSV Storage Implementation

The CSV storage service will:

1. Create the CSV file if it doesn't exist
2. Append new lead information to the file
3. Provide functions to read, update, and filter lead data
4. Handle data validation and error cases

### 9. Handoff

**Purpose**: Conclude conversation and set expectations for next steps.

**Example Prompt**:
```
Thanks for sharing your details! I've created a request for our pre-sales team. They'll get in touch soon.
```

**Actions**:
- Store all collected information in CSV storage
- Generate lead record
- End conversation

## Error Handling

The conversation flow includes error handling for various scenarios:

1. **Unclear Responses**: If the user's response is unclear, the chatbot will ask for clarification while remaining in the current state.

2. **Missing Information**: If critical information is missing, the chatbot will prompt specifically for that information.

3. **Topic Changes**: If the user changes the topic mid-conversation, the chatbot will acknowledge the change and adapt the flow accordingly.

4. **Conversation Restart**: If the user wants to start over, the chatbot will reset to the Greeting state.

## Implementation in Langflow

In Langflow, this conversation flow will be implemented using:

1. **State Management Nodes**: Track the current conversation state
2. **Intent Recognition Nodes**: Identify user intents from messages
3. **Entity Extraction Nodes**: Extract key information (project type, timeline, etc.)
4. **Response Generation Nodes**: Generate appropriate responses based on state
5. **Transition Logic Nodes**: Determine the next state based on current state and user input

Each state will have its own set of prompts, expected responses, and transition logic implemented as nodes in the Langflow graph. 