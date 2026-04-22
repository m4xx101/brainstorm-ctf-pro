# PDF Attack Patterns

PDF processing vulnerabilities across document AI systems.

## Attack Surface 1: Hidden Text
- White-on-white text at fontsize 0.1-0.2
- Processed by AI during OCR/document analysis, invisible to humans
- Effectiveness: 60-85% on document processors

## Attack Surface 2: Metadata Injection
- Title, Author, Subject, Creator, Keywords fields
- Many AI systems read metadata and incorporate into context
- Effectiveness: 40-70%

## Attack Surface 3: Annotations
- Text annotations (Notes, Comments) in PDF objects
- Effectiveness: 30-60% depending on PDF processor

## Attack Surface 4: Embedded JavaScript (legacy)
- PDF JS execution in processors that support it
- Most modern systems strip JS
- Effectiveness: 10-30%

## PDF Processor-Specific
- Resume parsers (Workday, Greenhouse): read hidden text + metadata
- Document analyzers (GPT-4V, Gemini Vision): read all text layers
- Research assistants: may read annotations
- Chat interfaces with file upload: typically reads main text layer + metadata
