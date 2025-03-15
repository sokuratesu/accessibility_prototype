"""
Report generators for accessibility testing results.
"""

import os
from datetime import datetime

import jinja2
from openpyxl import Workbook

template_loader = jinja2.FileSystemLoader(searchpath=os.path.join(os.getcwd(), "html_templates"))
template_env = jinja2.Environment(loader=template_loader)

summary_template = template_env.get_template("combined-report.html")
enhanced_summary_template = template_env.get_template("enhanced-summary-report.html")

def generate_html_report(results):
    """Generate HTML report from test results."""
    template = template_env.get_template(f"{results["tool"]}.html")
    return template.render(results=results)


def generate_excel_report(results, output_path):
    """Generate Excel report with multiple sheets from test results."""
    # Create a new workbook
    wb = Workbook()

    # Get the active sheet
    summary_sheet = wb.active
    summary_sheet.title = "Summary"

    # Add summary information
    summary_sheet["A1"] = "Accessibility Test Report"
    summary_sheet["A3"] = "URL"
    summary_sheet["B3"] = results.get("url", "Unknown")
    summary_sheet["A4"] = "Tool"
    summary_sheet["B4"] = results.get("tool", "Unknown")
    summary_sheet["A5"] = "Date"
    summary_sheet["B5"] = results.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # If there's an error, just show that and return
    if "error" in results:
        summary_sheet["A7"] = "Error"
        summary_sheet["B7"] = results["error"]
        wb.save(output_path)
        return

    # Handle tool-specific data
    tool = results.get("tool", "unknown")

    if tool == "axe-core":
        # Create sheets for violations, passes, etc.
        violations_sheet = wb.create_sheet("Violations")
        passes_sheet = wb.create_sheet("Passes")
        incomplete_sheet = wb.create_sheet("Incomplete")

        # Add violations data
        if "violations" in results:
            violations_sheet.append(["ID", "Description", "Impact", "WCAG Tags", "Affected Elements"])
            for violation in results["violations"]:
                violations_sheet.append([
                    violation.get("id", ""),
                    violation.get("help", ""),
                    violation.get("impact", ""),
                    ", ".join(violation.get("tags", [])),
                    len(violation.get("nodes", []))
                ])

        # Add similar data for passes and incomplete
        # (Implementation omitted for brevity)

    elif tool == "wave":
        # Create sheets for different WAVE categories
        errors_sheet = wb.create_sheet("Errors")
        alerts_sheet = wb.create_sheet("Alerts")
        features_sheet = wb.create_sheet("Features")

        # Add data from WAVE results
        # (Implementation omitted for brevity)

    elif tool == "japanese_a11y":
        # Create sheets for Japanese-specific tests
        japanese_sheet = wb.create_sheet("Japanese Tests")

        if "results" in results:
            # Add headers
            japanese_sheet.append(["Test Type", "Issues Found", "Details"])

            # Add data for each test type
            for test_name, test_data in results["results"].items():
                if isinstance(test_data, dict):
                    issues_found = test_data.get("issues_found", "N/A")
                    details = str(test_data.get("details", "No details"))
                    japanese_sheet.append([test_name, issues_found, details])

    # Save the workbook
    wb.save(output_path)
    return output_path


def generate_summary_report(all_results, main_test_dir):
    """Generate summary report of all tested pages."""
    all_results["total_issues"] = 0

    #Total up the issues for each page and the test as a whole
    for url, page_results in all_results["pages"].items():
        page_results["total_issues"] = 0
        for tool, results in page_results["tools"].items():
            page_results["total_issues"] += results["total_issues"]
        all_results["total_issues"] += page_results["total_issues"]

    html_report = summary_template.render(summary=all_results)

    # Save HTML report
    output_path = os.path.join(main_test_dir, "summary_report.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_report)

    return output_path


def generate_enhanced_summary_report(results: dict, main_test_dir: str) -> str:
    html_report = enhanced_summary_template.render(results=results)

    output_path = os.path.join(main_test_dir, "enhanced_summary.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    return output_path