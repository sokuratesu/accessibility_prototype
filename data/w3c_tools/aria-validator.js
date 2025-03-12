
// ARIA Validator JavaScript
function validateARIA() {
    const allElements = document.querySelectorAll('*');
    const issues = [];

    const ariaRoles = [
        'alert', 'alertdialog', 'application', 'article', 'banner', 'button', 'cell', 'checkbox', 
        'columnheader', 'combobox', 'complementary', 'contentinfo', 'definition', 'dialog', 
        'directory', 'document', 'feed', 'figure', 'form', 'grid', 'gridcell', 'group', 'heading', 
        'img', 'link', 'list', 'listbox', 'listitem', 'log', 'main', 'marquee', 'math', 'menu', 
        'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'navigation', 'none', 'note', 
        'option', 'presentation', 'progressbar', 'radio', 'radiogroup', 'region', 'row', 'rowgroup', 
        'rowheader', 'scrollbar', 'search', 'searchbox', 'separator', 'slider', 'spinbutton', 
        'status', 'switch', 'tab', 'table', 'tablist', 'tabpanel', 'term', 'textbox', 'timer', 
        'toolbar', 'tooltip', 'tree', 'treegrid', 'treeitem'
    ];

    allElements.forEach(el => {
        // Check for invalid ARIA roles
        const role = el.getAttribute('role');
        if (role && !ariaRoles.includes(role)) {
            issues.push({
                element: el.tagName,
                id: el.id,
                class: el.className,
                issue: `Invalid ARIA role: ${role}`,
                severity: 'serious',
                wcag: 'ARIA4'
            });
        }

        // Check for ARIA attributes on elements that don't support them
        const hasAriaAttrs = Array.from(el.attributes).some(attr => attr.name.startsWith('aria-'));
        if (hasAriaAttrs && ['meta', 'br', 'style', 'script'].includes(el.tagName.toLowerCase())) {
            issues.push({
                element: el.tagName,
                id: el.id,
                class: el.className,
                issue: `ARIA attributes used on element that does not support them`,
                severity: 'critical',
                wcag: 'ARIA2'
            });
        }

        // Check for required ARIA attributes based on role
        if (role === 'checkbox' || role === 'radio') {
            if (!el.hasAttribute('aria-checked')) {
                issues.push({
                    element: el.tagName,
                    id: el.id,
                    class: el.className,
                    issue: `Missing required aria-checked attribute for ${role}`,
                    severity: 'serious',
                    wcag: 'ARIA8'
                });
            }
        }

        // Check for proper aria-labelledby references
        const labelledby = el.getAttribute('aria-labelledby');
        if (labelledby) {
            const ids = labelledby.split(/\s+/);
            ids.forEach(id => {
                if (!document.getElementById(id)) {
                    issues.push({
                        element: el.tagName,
                        id: el.id,
                        class: el.className,
                        issue: `aria-labelledby references non-existent ID: ${id}`,
                        severity: 'critical',
                        wcag: 'ARIA16'
                    });
                }
            });
        }

        // Check for proper use of ARIA in focusable elements
        if (el.hasAttribute('tabindex') && parseInt(el.getAttribute('tabindex')) >= 0) {
            if (role === 'presentation' || role === 'none') {
                issues.push({
                    element: el.tagName,
                    id: el.id,
                    class: el.className,
                    issue: `Focusable element with presentation/none role`,
                    severity: 'serious',
                    wcag: 'ARIA6'
                });
            }
        }

        // Check for ARIA attributes that require specific roles
        if (el.hasAttribute('aria-pressed') && (role !== 'button')) {
            issues.push({
                element: el.tagName,
                id: el.id,
                class: el.className,
                issue: `aria-pressed used on element without button role`,
                severity: 'moderate',
                wcag: 'ARIA8'
            });
        }

        // Check for ARIA 1.1 features
        if (el.hasAttribute('aria-errormessage')) {
            const errorId = el.getAttribute('aria-errormessage');
            const errorElement = document.getElementById(errorId);
            if (errorElement && !errorElement.hasAttribute('aria-live')) {
                issues.push({
                    element: el.tagName,
                    id: el.id,
                    class: el.className,
                    issue: `Element referenced by aria-errormessage should have aria-live attribute`,
                    severity: 'moderate',
                    wcag: 'ARIA19'
                });
            }
        }
    });

    return {
        issues: issues,
        count: issues.length
    };
}

return validateARIA();
