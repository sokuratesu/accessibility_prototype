Accessibility Testing Tool
A comprehensive accessibility testing framework built in Python to evaluate websites against WCAG 2.2 AA standards, using multiple testing engines and methodologies.
Features

Multi-Engine Testing: Integrates with multiple accessibility testing tools including Axe, WAVE, Pa11y, HTML CodeSniffer, and custom W3C tools
WCAG 2.2 Focused: Custom tests specifically designed for newer WCAG 2.2 AA success criteria
W3C Tools Integration: Built-in support for W3C validators and accessibility checkers
Selective Testing: Configure which specific tests to run for optimal performance
Comprehensive Reports: Detailed HTML and JSON reports with issue categorization
User-Friendly Interface: Easy-to-use Flet-based UI for configuring and running tests

Installation
Prerequisites

Python 3.7+
Google Chrome (for headless testing)
Node.js (for Pa11y)


Usage
Running from the UI
Start the application with:
Copypython -m src.main
The UI allows you to:

Enter a URL to test
Select which testing tools to use
Configure W3C accessibility tools
Run WCAG 2.2 specific tests
View and export results

W3C Tools Configuration
The W3C tools section allows you to selectively run:

HTML Validator
CSS Validator
Link Checker
Nu HTML Checker (requires Java)
ARIA Validator
DOM Accessibility

Reports
Reports are generated in the Reports directory and include:

JSON reports with detailed testing data
HTML reports with visualizations and issue breakdowns
Summary of issues by category and severity

Manual Testing Integration
The tool also provides structured templates for manual testing activities:

Keyboard navigation testing
Screen reader compatibility
Visual and cognitive testing
Mobile accessibility

WCAG 2.2 Coverage
The tool specifically tests for the newest WCAG 2.2 AA success criteria:

2.4.11 Focus Not Obscured (Minimum)
2.5.7 Dragging Movements
2.5.8 Target Size (Minimum)
3.2.6 Consistent Help
3.3.7 Accessible Authentication
3.3.9 Redundant Entry

Development
Project Structure
Copyaccessibility-tester/
├── src/
│   ├── core/
│   │   ├── test_orchestrator.py
│   │   └── base_tester.py
│   ├── testers/
│   │   ├── axe_tester.py
│   │   ├── wave_tester.py
│   │   ├── pa11y_tester.py
│   │   ├── htmlcs_tester.py
│   │   ├── w3c_tester.py
│   │   └── wcag22_tester.py
│   ├── ui/
│   │   └── app.py
│   ├── utils/
│   │   ├── report_generators.py
│   │   └── crawler.py
│   └── main.py
├── data/
│   └── w3c_tools/
│       └── aria-validator.js
├── docs/
│   ├── manual_test_plan.md
│   └── tester_guidance.md
└── requirements.txt
Adding New Testing Tools
To add a new testing tool:

Create a new tester class in the src/testers directory
Inherit from BaseAccessibilityTester
Implement the test_accessibility method
Register the tester in src/core/test_orchestrator.py

License
This project and code belongs to ASA DIGITAL.