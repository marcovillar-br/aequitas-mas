@workspace
As my AI Developer (GCA), update the model name in `src/agents/fisher.py`.

Error Context: The Google Generative AI API returned a 404 error because the model `gemini-1.5-flash` has been deprecated.

Task Instructions:
1. Open `src/agents/fisher.py`.
2. Locate the initialization of the `ChatGoogleGenerativeAI` model.
3. Change the `model` parameter strictly from `"gemini-1.5-flash"` (or `"gemini-1.5-flash-latest"`) to `"gemini-2.5-flash"`.
4. Keep the `temperature=0.1` and all other logic intact.
5. All code, variables, and comments must remain in English.