# Live platform completion

Use the hackathon-approved project from the GitLab contributor application, not an unrelated private research repository. The default branch must contain agent-config.yml because GitLab reads that file only from the default branch.

The custom flow YAML belongs in an AI Catalog flow definition; committing the YAML alone does not register a flow. Enable the flow for the project, select the mention/reviewer trigger supported by that project, and retain the actual session link. The flow may run tests/audit/package but must leave manual release to the human.

For the recorded platform demonstration:

1. Commit the correct billing implementation and show a passing test/verify/package pipeline.
2. Open a merge request changing the return to `units * (unit_price + shipping)`. The sample free-shipping tests still pass; exact verification reports REFUTED and blocks downstream artifacts.
3. Ask the enabled Duo flow to review that merge request. Show its executed commands and actual counterexample, rather than a prepared transcript.
4. Replace the change with `shipping + unit_price * units`; run the pipeline and flow again. Inspect the package's receipt. Keep the manual release button visible and unclicked until a real human release decision.

Current access: an approved project URL has not been provided. Local tests and the web demo are already executable without GitLab credentials.

Official references, checked 8 October 2026:

- https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/
- https://docs.gitlab.com/user/duo_agent_platform/flows/execution/
- https://docs.gitlab.com/user/duo_agent_platform/flows/execution/images/
- https://gitlab-transcend.devpost.com/resources
