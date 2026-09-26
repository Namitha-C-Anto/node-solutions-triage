# AI Request Triage Assistant

A prototype that takes an unstructured client request and returns a summary, category, priority (with reasoning), owner assignment, and a draft first response — built for the Node Solutions Stage Two challenge.

## Demo

🔗 **Live app:** [node-solutions-triage-namitha.streamlit.app](https://node-solutions-triage-namitha.streamlit.app/)

## Running locally

`streamlit run app.py` — paste a request, or load one of the 6 mock requests from the sidebar dropdown.

## Approach

The brief asks for six distinct outputs per request (summary, category, priority + reason, routing, draft response). Rather than building a multi-agent pipeline (e.g. separate classify → route → draft agents), I used **one structured LLM call** that returns all six fields at once, enforced by a Pydantic schema.

**Why:** given the 48-hour window and the challenge's own guidance ("a focused working prototype is better than a large unfinished system"), a single reliable call reduces failure points and latency compared to chaining multiple LLM calls. The tradeoff is less separation of concerns — if I were building this for production scale, I'd likely split classification and drafting into separate calls so each could be tuned and evaluated independently.

## Stack

- **Groq** (`openai/gpt-oss-120b`) for inference — fast, free-tier friendly, good fit for a time-boxed prototype
- **LangChain** (`ChatPromptTemplate` + `with_structured_output`) to wire the prompt to a Pydantic schema
- **Streamlit** for the UI — fastest path to a usable interface without frontend work
- **Pydantic** to define and validate the output schema

## Schema

```python
class TriageResult(BaseModel):
    summary: str
    category: Literal["Sales", "Support", "Billing", "Technical", "Other"]
    priority: Literal["Low", "Medium", "High", "Urgent"]
    priority_reason: str
    routed_to: Literal["Sales Team", "Client Success", "Finance", "Engineering"]
    draft_response: str
```

Using `Literal` types (rather than free-text strings) means the model's output is constrained to only the valid options at the schema level, not just by prompt instruction.

## Prompt design decisions

The prompt encodes explicit rules rather than relying on the model to infer them, particularly for the two trickiest mock requests:
## Prompt design decisions

The prompt encodes explicit rules rather than relying on the model to infer them, particularly for the two trickiest mock requests:

- **Security/data incidents are always Urgent**, regardless of whether a deadline is stated. Request #05 (accidental data exposure) has no explicit urgency language, but a data leak is objectively urgent — this rule catches that case rather than relying on tone.
- **Priority ≠ category.** An outage (#02) and a data leak (#05) are both "Technical," but the priority reasoning is spelled out separately so the model explains *why* each is urgent, not just *that* it is.
- **Low vs. Medium is a genuinely ambiguous boundary, and my rule wording didn't fully resolve it.** A routine, non-blocking question ("is there a way to export as CSV instead of PDF... not blocking anything, just easier") consistently came back as Medium rather than Low — even after I explicitly added phrases like "not blocking anything" and "just easier" to the Low rule's own wording. On reflection, I think the model's behavior may actually be reasonable: a genuine, actionable ask (even a low-stakes one) arguably *is* still Medium, and Low is better reserved for requests explicitly framed as ideas or future wishlist items, like mock request #04's own framing ("I am collecting ideas for a future update"). I left the broader rule wording in place rather than rewriting it again, since tightening it further didn't change the outcome in my testing — this is a known imprecision in the prompt that I'm flagging rather than claiming is fully solved.

## Limitations

- No integration with a real inbox, web form, or chat system — input is manual/pasted text only.
- No automated evaluation set — testing was manual, against the 6 mock requests plus a handful of custom edge cases (ambiguous urgency, mixed-category requests, informal phrasing).
- No retry/fallback logic if the Groq API errors or rate-limits.
- Draft responses don't pull in real client name/history — they're generic first-touch templates.
- No logging or observability — a production version would need to track classification accuracy over time and flag low-confidence outputs for human review.

## What I'd improve next

- Build a small labeled eval set (10-20 requests with expected outputs) to catch prompt regressions when rules change.
- Add confidence scoring or a "needs human review" flag for borderline cases, rather than always returning a single confident answer.
- **Agentic intake layer:** right now, requests are entered manually. In production, an agentic layer could poll a shared inbox or listen on a webhook from the website's contact form, extract the request text automatically, run it through this same triage pipeline, and only notify a human when priority is High or Urgent — turning this from a tool someone has to remember to use into something that runs on its own. I intentionally didn't build this now, since the challenge scopes input to the provided mock requests and discourages spending time/money on real integrations — but it's a natural next step given the JD's emphasis on connecting existing systems.
- **RAG over real SOP documents:** classification and routing rules are currently hardcoded into the prompt. If this were adopted for real, those rules would likely live in the company's actual SOP documents, which change over time and are maintained by non-engineers. A natural next step would be to retrieve the relevant SOP section for each incoming request — similar to a RAG-based knowledge assistant — rather than relying on a single static prompt to encode every rule. This would let policy updates happen without needing to touch code.
- Separate classification and draft-response generation into two calls if response quality and classification accuracy need to be tuned independently.