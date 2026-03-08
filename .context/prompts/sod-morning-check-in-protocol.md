### Morning Check-in Protocol (Aequitas-MAS V2.0 Optimized)

**Role:** Senior Architect & SOTA Engineer (Aequitas-MAS)

**Task:** Execute Morning Check-in Protocol (Daily Initialization and State Validation)

**Instructions:**

1. **Context Loading:** Perform a full recursive sweep of the `.context/` directory. Prioritize the review of `sod-context-enforcement.md`, `setup.md`, and `coding-guidelines.md` to ensure architectural alignment.
2. **Skill Synchronization:** Map and mental-load all capabilities from `.context/agents/skills-index.md`.
3. **Mandatory Architecture Audit (V2.0 Dogmas):** Before proceeding with any coding, verify the current system isomorphism against `src/core/state.py` and the `setup.md` status table. You MUST actively check for:
   * **Controlled Degradation:** Ensure Pydantic V2 state schemas utilize `Optional[float] = None` for financial metrics. Flag any usage of `Decimal`, as it breaks LangGraph state serialization.
   * **Dependency Inversion Principle (DIP):** Ensure no infrastructure SDKs (e.g., `import boto3`) are present inside the `/src/agents/` directory.
   * **Zero Numerical Hallucination:** Confirm that all quantitative reasoning is delegated to strictly typed, `pytest`-covered Python tools (e.g., `src/tools/`).
4. **Language Enforcement:** Follow the updated **Section 4 (Language and Localization Protocol)**:
   * Internal reasoning and logic processing may occur in English.
   * **ALL final outputs**, technical explanations, Chain of Thought (CoT), and academic reports MUST be delivered strictly in **Brazilian Portuguese (pt-BR)**.
   * Maintain technical terms (e.g., *State Machine*, *Backtesting*, *Optional[float]*) in English, but use formal academic pt-BR (UFG/USP ESALQ style) for the surrounding context.

## IDE Interaction Protocol (GCA Prompting)

When utilizing the Gemini Code Assist (GCA) chat in the IDE, the Tech Lead will use the following standard prompt format to anchor the AI's context. GCA must strictly obey this operational boundary:

> "GCA, read `.context/rules/coding-guidelines.md` for the strict project guidelines. Based on the attached `@SPEC.md` and `@PLAN.md`, execute exclusively **Step [Number]**. Focus only on this atomic task (following the RPI methodology). Remember the Risk Confinement: do not calculate metrics mentally, enforce `Optional[float] = None`, and do not use Cloud SDKs in Agents. Wait for my review before proceeding."

**Directive to GCA:** If you receive the prompt above, you must initialize your response by confirming that your execution scope is aligned with Aequitas-MAS guidelines. Do not generate code for subsequent steps until explicitly authorized by the Tech Lead.

**Required Output:**
Start the session by providing the **[Context Activated]** audit block, citing the rules and skills loaded, followed by a brief summary of the current project state in pt-BR.