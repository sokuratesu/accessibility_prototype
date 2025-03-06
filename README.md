# Accessibility Prototype

A comprehensive accessibility testing application for evaluating websites against various accessibility standards, including WCAG and JIS guidelines. Particularly focuses on Japanese accessibility requirements.

## Features

- Multiple testing engines:
  - Axe-core via Selenium
  - WAVE API
  - Japanese-specific accessibility testing
  - (More engines can be easily added)
- Website crawling to test multiple pages
- Comprehensive reporting (HTML, JSON, Excel)
- Japanese-specific testing features:
  - Ruby text (furigana) validation
  - Form Zero testing
  - Typography checks for Japanese text
  - IME support testing
- Customizable configuration
- User-friendly GUI built with Flet