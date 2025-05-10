# AI Artist Platform - Streamlit Dashboard UI/UX Specification (v1.4)

**Inspired by:** [Reference Dashboard Image](https://miro.medium.com/v2/resize:fit:1000/1*qalZbT0QnbRNiOnx2hXMnQ.png)

## 1. Goal

To upgrade the existing Streamlit dashboards (Batch Monitor, Release Management, Error Dashboard) with a more professional, modern, and cohesive user interface, drawing inspiration from the provided reference image.

## 2. Overall Layout & Navigation

*   **Layout:** Adopt a two-column layout similar to the reference:
    *   **Left Sidebar:** Fixed-width, dark background, used for primary navigation between dashboard sections.
    *   **Main Content Area:** Wider, light background, displays the selected dashboard content.
*   **Navigation:**
    *   Use `st.sidebar` for navigation links.
    *   Each link (e.g., "Overview", "Batch Monitor", "Release Management", "Error Dashboard", "Settings") should correspond to a distinct dashboard view.
    *   Consider using icons alongside text labels in the sidebar (using Streamlit-option-menu component or similar if needed for better styling, or simple emojis).
    *   The reference shows expandable sidebar sections ("Product", "Orders"); this could be used if sub-navigation becomes necessary, but start simple.

## 3. Color Scheme & Styling

*   **Sidebar:** Dark background (e.g., `#1E1E2D` or similar deep blue/purple), light text for navigation links, potentially an accent color for the selected/active link.
*   **Main Content Area:** Light background (e.g., `#F8F9FA` or white), dark text for content.
*   **Accent Colors:** Use accent colors sparingly for charts, key metric highlights, status indicators (e.g., blues, oranges, greens as seen in the reference).
*   **Components:** Style Streamlit components (buttons, tables, charts) to fit this theme. This might require custom CSS injected via `st.markdown(..., unsafe_allow_html=True)` for a production-grade look, as Streamlit's default styling is limited.
*   **Cards/Containers:** Use subtle borders, rounded corners, and slight shadows for containers holding metrics, charts, or tables, similar to the reference image, to create visual separation.

## 4. Key Metrics Display (Overview Page)

*   **Component:** Use `st.columns` to create a row of metric cards at the top of the main content area, similar to the reference.
*   **Styling:** Each column should contain an `st.metric` component.
    *   Display the metric label (e.g., "Total Artists", "Active Runs", "Errors Today").
    *   Display the main value prominently.
    *   Optionally display a delta or secondary value (e.g., change from last week) using the `delta` parameter of `st.metric`.
    *   Apply custom CSS to style these columns as distinct cards with appropriate background, padding, and rounded corners.

## 5. Charts & Visualizations

*   **Component:** Use Streamlit's native charting (`st.line_chart`, `st.bar_chart`, `st.area_chart`) or libraries like Plotly (`st.plotly_chart`) or Altair (`st.altair_chart`) for more customization.
*   **Styling:**
    *   Aim for clean lines and clear labels, matching the reference's aesthetic.
    *   Use the defined accent colors.
    *   Ensure charts are responsive.
    *   Place charts within styled containers/cards.
*   **Examples:**
    *   **Batch Monitor:** Line chart showing run statuses over time.
    *   **Error Dashboard:** Bar chart showing error frequency by type, line chart showing errors over time.
    *   **Release Management:** Potentially charts showing release frequency or content types.

## 6. Data Tables

*   **Component:** Use `st.dataframe` or `st.data_editor` (if editing is needed).
*   **Styling:**
    *   Apply custom CSS to match the reference's clean table style: subtle row dividers, clear headers, appropriate padding.
    *   Consider alternating row colors for readability if needed.
    *   Ensure tables are scrollable horizontally if they contain many columns.
*   **Examples:**
    *   **Batch Monitor:** Table listing recent runs with status, artist, timestamps.
    *   **Error Dashboard:** Table listing detailed error logs.
    *   **Release Queue:** Table showing queued releases.

## 7. Implementation Notes

*   **Modularity:** Structure the Streamlit app with separate Python files for each dashboard section/page, imported into a main app file.
*   **Custom CSS:** Achieving the polished look of the reference will likely require custom CSS. Store this in a separate `.css` file and load it using a function.
*   **Responsiveness:** While Streamlit handles basic responsiveness, test the layout on different screen sizes.

## 8. LLM Recommendation for Code Generation

For generating Streamlit code based on this specification, an LLM with strong Python coding capabilities and familiarity with the Streamlit library is recommended. Models like:

*   **GPT-4 / GPT-4o:** Known for strong code generation and understanding complex instructions.
*   **Claude 3 (Opus/Sonnet):** Also demonstrates excellent coding abilities.
*   **Gemini (Advanced/Pro):** Google's models are proficient in Python and can generate relevant code snippets.

**Prompting Strategy:** Provide the LLM with specific sections of this specification (e.g., "Generate Streamlit code for a sidebar navigation using st.sidebar based on these requirements...") and iterate on the generated code. Providing the reference image URL might also help the LLM understand the desired visual style.
