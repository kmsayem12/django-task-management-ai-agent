# 🤖 Agentic AI Implementation with The Django

##AI Chat API Documentation

This API allows you to interact with an AI agent (powered by LangGraph) to manage tasks using natural language.

---

## 📍 Endpoint

**URL:** `/api/ai/chat/`  
**Method:** `POST`  
**Auth Required:**

---

## 📥 Request

### Headers

Content-Type: application/json
Authorization: token <your_token>

### Generate Token

run `python generate-token.py`

### Body Parameters

| Key     | Type   | Required | Description                            |
| ------- | ------ | -------- | -------------------------------------- |
| message | string | ✅ Yes   | The natural language input for the AI. |

#### Example Request Payload

```json
{
  "message": "can you give me tasks list"
}
```

📤 Response

```json
{
  "data": [
    {
      "content": "Parsed message content or structured response",
      "name": "tool_name or AI",
      "status": "success | fallback | error | null",
      "tool_call_id": "UUID string or null"
    }
  ]
}
```

Sample Messages
You can send natural language messages like the following:

```json
{ "message": "can you give me tasks list" }
{ "message": "search the task title is 'Implement new feature' and limit is 5" }
{ "message": "delete the task title is 'My Task'" }
{ "message": "delete the task_id is 11" }
{ "message": "delete the task_id is 11" }
{ "message": "update the task title is 'Implement new feature for the about page design' and status is in_progress" }
{ "message": "can you create the task title is 'implementing a new feature for the search page refactor.' and description is 'test description'" }
```

🔄 Supported Intents
✅ Create Task

✅ Update Task by ID or Title

✅ Delete Task ID or Title

✅ Get All Tasks by login user

✅ Search Task by title or description

✅ Get Specific Task by ID or Title
