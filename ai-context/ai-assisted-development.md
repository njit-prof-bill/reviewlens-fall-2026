# AI-Assisted Development and Review

AI-generated code is team-authored code. It carries the same Definition of Done,
the same review standard, and the same accountability as anything typed by hand.
"The assistant wrote it" is not an explanation for a defect.

## 1. Tools

GitHub Copilot in VS Code (chat and inline) is the expected assistant. Any other
tool is fine provided the expectations below are met and the session transcript
can be retained.

## 2. Context to supply

Before asking for anything non-trivial, point the assistant at the files that
constrain the answer. Attaching them beats describing them.

| Working on                 | Supply                                                                                                              |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Anything                   | `ai-context/coding-standards.md`, `ai-context/architecture-brief.md`                                                |
| User data, auth, ownership | `ai-context/security-guardrails.md`                                                                                 |
| UI                         | `ai-context/ui-ux-standards.md`, `docs/Requirements/ReviewLens-UX-Implementation-Reference.md`, the wireframe image |
| API surface                | `ai-context/api-conventions.md`                                                                                     |
| Sprint scope               | The current sprint stories file                                                                                     |
| Infrastructure             | `ai-context/iaas-standards.md`                                                                                      |

Also supply the story id you are implementing and the neighbouring code the
change must match. Generated code that ignores existing patterns is the most
common source of rework.

## 3. Reviewing generated code

Read every line before committing it. In particular:

- **Ownership.** Does every user-scoped query filter on the authenticated owner?
  Assistants routinely produce `db.get(Model, id)` without a tenant filter. This
  is the single highest-risk failure mode in this codebase.
- **Invented behaviour.** Does the code fabricate data to make a path succeed?
  Placeholder reviews, stubbed counts, and hard-coded sample records violate
  S1-BR-024 and will fail the demo.
- **Error handling.** Are provider messages, tracebacks, or credentials able to
  reach a response body?
- **Scope.** Does the diff do only what the story asked? Delete unrequested
  extras rather than keeping them because they look useful.
- **Consistency.** Does it use the existing service layer, error envelope, and
  component primitives rather than introducing a parallel approach?

If you cannot explain a line to a teammate, do not commit it. You will be asked
to explain it during the sprint demo.

## 4. Validating generated dependencies and APIs

Assistants confidently cite packages and methods that do not exist.

- Confirm any new dependency actually exists, is maintained, and is not a
  typosquat. Prefer what is already in `package.json` or `pyproject.toml`.
- Adding a dependency needs a reason a reviewer would accept. A handful of lines
  is cheaper than a supply-chain surface.
- Verify library calls against real documentation, not against the assistant's
  recollection. Version drift is common; check the version we actually pin.
- Verify third-party API request and response shapes against the vendor's docs,
  then record a real response as a test fixture.

## 5. Testing before acceptance

Generated code is not accepted until:

1. It has at least one automated test that would fail without the change.
2. Tests exercise observable behaviour, not implementation details.
3. Auth and ownership changes include the negative paths from
   `security-guardrails.md` section 9.
4. Ingestion or parsing changes are tested against committed fixtures, never a
   live third-party call.
5. The full suite passes locally and in CI.

Do not accept an assistant's claim that code works. Run it.

## 6. Transcript retention

Keep a session log per significant piece of work in
`docs/development-logs/`, named `<n>-<topic>.txt`. Record the prompts that
mattered, decisions taken, and rejected alternatives. These logs are project
deliverables and are what lets another developer understand why the code looks
the way it does.

## 7. When extra security review is required

A second reviewer looks at any generated change that touches:

- authentication, token verification, or session handling
- ownership filters or authorization checks
- secret loading, environment configuration, or credential handling
- raw SQL, dynamic query construction, or file-path handling
- file upload parsing
- outbound requests to third-party services
- CORS, CSP, or other response headers
- anything that changes what appears in an error response

## 8. What must not be delegated

- Pasting real secrets, tokens, or production data into a prompt.
- Accepting a security control you do not understand.
- Generating tests that assert current behaviour without asking whether that
  behaviour is correct.
- Bulk-generating code across many files in a single unreviewed commit.
