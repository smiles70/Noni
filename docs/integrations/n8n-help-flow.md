# n8n Help Flow Integration

This document describes the production n8n workflow that receives help requests from the Mynaani backend and routes them according to the N8N-HELP-001 requirements.

## Webhook endpoint

Mynaani POSTs to the configured `N8N_WEBHOOK_URL` (for example `https://<your-workspace>.app.n8n.cloud/webhook/mynaani-help`) with the following JSON body:

```json
{
  "request_id": "uuid-string",
  "context": "caregiver" | "facility",
  "category": "buying_gift" | "payment_issue" | ...,
  "sub_category": null,
  "severity": "P3",
  "reply_email": "user@example.com",
  "message": "Plain text message",
  "page_path": "/gift",
  "client_ip": "203.0.113.1",
  "created_at": "2026-09-11T22:12:33.823243+00:00"
}
```

If `N8N_WEBHOOK_TOKEN` is set on the backend, the request includes an `X-N8N-Auth: <token>` header.

## n8n workflow design

The n8n workflow is responsible for:

1. Receiving the webhook.
2. Validating `X-N8N-Auth` (optional but recommended).
3. Branching by `context` (caregiver vs facility).
4. Mapping `category` to an initial support severity and SLA.
5. Returning a calm auto-acknowledgment to the backend.
6. Notifying support through the appropriate channel (email, Slack, ticket system).

### Recommended node layout

```
Webhook (POST, path: mynaani-help, Response: Respond to Webhook)
  ├─ If / Switch on context
       ├─ context = caregiver
       │     ├─ Switch on category
       │     ├─ Respond to Webhook with caregiver auto-ack
       │     ├─ Send Email / Slack to caregiver-support queue
       │
       └─ context = facility
             ├─ Switch on category
             ├─ Respond to Webhook with facility auto-ack
             ├─ Send Email / Slack to b2b-support queue
```

### Category severity mapping

| Category | Context | Severity | Response target | Initial response text (example) |
|---|---|---|---|---|
| `buying_gift` | caregiver | P3 (low) | 1 week | "Thank you. A mynaani gift is $39.00. We will send your gift code to the email you provide at checkout." |
| `payment_issue` | caregiver | P1 (high) | 8 hours | "Thank you. We received your payment question and will get back to you within 8 hours." |
| `gift_not_received` | caregiver | P0/P1 | 2-8 hours | "Thank you. We received your message about the missing gift and will respond quickly." |
| `redeeming_gift` | caregiver | P2 | 48 hours | "Thank you. We received your gift-redeem question and will reply within 48 hours." |
| `managing_recipient_access` | caregiver | P2 | 48 hours | "Thank you. We received your access question and will reply within 48 hours." |
| `partnership_inquiry` | facility | P2 | 48 hours | "Thank you. We received your partnership question and will reply within 48 hours." |
| `licensing_and_seats` | facility | P2 | 48 hours | "Thank you. We received your licensing question and will reply within 48 hours." |
| `billing_and_invoice` | facility | P1 | 8 hours | "Thank you. We received your billing question and will reply within 8 hours." |
| `technical_setup` | facility | P1 | 8 hours | "Thank you. We received your setup question and will reply within 8 hours." |
| `something_else` | either | P3 | 1 week | "Thank you. We received your message and will reply within one week." |

### Auto-acknowledgment payload

Set the **Webhook** node to **Response Mode: Using 'Respond to Webhook' Node**, then add a **Respond to Webhook** node whose JSON body depends on category. For `buying_gift`, a useful response is:

```json
{
  "status": "received",
  "message": "Thank you. A mynaani gift is $39.00. We will send the gift code to the email you provide at checkout."
}
```

### Product pricing

The current paid bundle is `modules_4_5` at **$39.00 USD** (3,900 cents). Use this value in the `buying_gift` auto-ack. If pricing changes, update the response text here or switch to an **HTTP Request** node that calls the Mynaani backend for the current price.

### Support routing

For categories that need human follow-up, add a **Send Email** or **Slack** node after the auto-ack. Suggested recipients:

- `support@mynaani.com` for caregiver issues
- `partnerships@mynaani.com` for facility partnership or licensing questions

Include the original `message`, `email`, `context`, `category`, `page_path`, and `request_id` in the notification so support can identify the request without re-asking.

### Security

To prevent public requests to the n8n webhook, use the **Header Auth** option on the Webhook node:

- **Name:** `X-N8N-Auth`
- **Value:** the same value stored in the Railway `N8N_WEBHOOK_TOKEN` environment variable.

If Header Auth is enabled in n8n, set `N8N_WEBHOOK_TOKEN` on both the `noni-api` and `noni-worker` Railway services to the same value.

## Mynaani side: where the message goes

1. The user submits the widget on `/gift`, `/for-communities`, `/org`, or `/c/:slug`.
2. The backend validates the request, stores it in the `support_requests` table, and writes an audit row.
3. The backend enqueues `deliver_help_request_to_n8n` in Celery.
4. The `noni-worker` service picks up the task and POSTs the payload to the n8n webhook.
5. n8n returns the auto-acknowledgment JSON, which the worker records.
6. The n8n workflow separately routes the request to the appropriate support channel.

## Step-by-step n8n setup for the `mynaani-help` workflow

1. Open **Workflows** → **New workflow**.
2. Click the **+** icon and search **Webhook**. Add a **Webhook** node.
   - **Method:** POST
   - **Path:** `mynaani-help`
   - **Authentication:** None (or **Header Auth** if you set `N8N_WEBHOOK_TOKEN`)
   - **Header Name (if using Header Auth):** `X-N8N-Auth`
   - **Response:** `Using 'Respond to Webhook' Node`
3. Add a **Switch** node after the Webhook. Set the value to `{{ $json.context }}`.
   - **Case 1:** `caregiver`
   - **Case 2:** `facility`
   - **Fallback:** continue to a default branch
4. In the `caregiver` branch, add a second **Switch** node. Set the value to `{{ $json.category }}`.
   - For **Output 1** (`buying_gift`), connect a **Respond to Webhook** node with this JSON:
     ```json
     {
       "status": "received",
       "message": "Thank you. A mynaani gift is $39.00. We will send the gift code to the email you provide at checkout."
     }
     ```
   - For **Output 2** (`payment_issue`), connect a **Respond to Webhook** node:
     ```json
     { "status": "received", "message": "Thank you. We received your payment question and will get back to you within 8 hours." }
     ```
   - For all other categories, choose the matching response text from the table above.
5. Repeat the same pattern for the `facility` branch using the facility category map.
6. After each **Respond to Webhook** node, add a **Send Email** or **Slack** node for human follow-up. Use the `reply_email`, `message`, `category`, `severity`, and `request_id` fields.
7. Save and **Activate** the workflow.
8. Copy the **Production URL** and set it as `N8N_WEBHOOK_URL` in Railway for both `noni-api` and `noni-worker` if it changed.

## Testing

1. Publish the n8n workflow.
2. Submit a request on `https://staging.noni-web.pages.dev/gift`.
3. Check the **Executions** tab in n8n for the received payload.
4. Verify the auto-ack response and any email/Slack notification nodes.
