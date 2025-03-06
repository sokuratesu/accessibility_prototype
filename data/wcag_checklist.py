"""
WCAG Checklist data
This module contains the WCAG checklist data used for accessibility testing.
"""

WCAG_CHECKLIST = {
    "Perceivable": {
        "1.1 Text Alternatives": {
            "1.1.1": {
                "level": "A",
                "title": "Non-text Content",
                "description": "All non-text content has a text alternative that serves the equivalent purpose."
            }
        },
        "1.2 Time-based Media": {
            "1.2.1": {
                "level": "A",
                "title": "Audio-only and Video-only (Prerecorded)",
                "description": "Provide alternatives for time-based media."
            },
            "1.2.2": {
                "level": "A",
                "title": "Captions (Prerecorded)",
                "description": "Captions are provided for all prerecorded audio content in synchronized media."
            },
            "1.2.3": {
                "level": "A",
                "title": "Audio Description or Media Alternative (Prerecorded)",
                "description": "Alternative for time-based media or audio description provided."
            },
            "1.2.4": {
                "level": "AA",
                "title": "Captions (Live)",
                "description": "Captions are provided for all live audio content in synchronized media."
            },
            "1.2.5": {
                "level": "AA",
                "title": "Audio Description (Prerecorded)",
                "description": "Audio description is provided for all prerecorded video content."
            },
            "1.2.6": {
                "level": "AAA",
                "title": "Sign Language (Prerecorded)",
                "description": "Sign language interpretation is provided for all prerecorded audio content."
            },
            "1.2.7": {
                "level": "AAA",
                "title": "Extended Audio Description (Prerecorded)",
                "description": "Extended audio description is provided for all prerecorded video content."
            },
            "1.2.8": {
                "level": "AAA",
                "title": "Media Alternative (Prerecorded)",
                "description": "Alternative for time-based media is provided for all prerecorded synchronized media and video-only media."
            },
            "1.2.9": {
                "level": "AAA",
                "title": "Audio-only (Live)",
                "description": "Alternative for time-based media is provided for all live audio-only content."
            }
        },
        "1.3 Adaptable": {
            "1.3.1": {
                "level": "A",
                "title": "Info and Relationships",
                "description": "Information, structure, and relationships conveyed through presentation can be programmatically determined."
            },
            "1.3.2": {
                "level": "A",
                "title": "Meaningful Sequence",
                "description": "When the sequence in which content is presented affects its meaning, a correct reading sequence can be programmatically determined."
            },
            "1.3.3": {
                "level": "A",
                "title": "Sensory Characteristics",
                "description": "Instructions provided for understanding and operating content do not rely solely on sensory characteristics."
            },
            "1.3.4": {
                "level": "AA",
                "title": "Orientation",
                "description": "Content does not restrict its view and operation to a single display orientation."
            },
            "1.3.5": {
                "level": "AA",
                "title": "Identify Input Purpose",
                "description": "The purpose of each input field collecting information about the user can be programmatically determined."
            },
            "1.3.6": {
                "level": "AAA",
                "title": "Identify Purpose",
                "description": "The purpose of User Interface Components, icons, and regions can be programmatically determined."
            }
        },
        "1.4 Distinguishable": {
            "1.4.1": {
                "level": "A",
                "title": "Use of Color",
                "description": "Color is not used as the only visual means of conveying information."
            },
            "1.4.2": {
                "level": "A",
                "title": "Audio Control",
                "description": "If any audio plays automatically for more than 3 seconds, either a mechanism is available to pause or stop the audio, or a mechanism is available to control audio volume."
            },
            "1.4.3": {
                "level": "AA",
                "title": "Contrast (Minimum)",
                "description": "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1."
            },
            "1.4.4": {
                "level": "AA",
                "title": "Resize text",
                "description": "Text can be resized without assistive technology up to 200 percent without loss of content or functionality."
            },
            "1.4.5": {
                "level": "AA",
                "title": "Images of Text",
                "description": "If the technologies being used can achieve the visual presentation, text is used to convey information rather than images of text."
            },
            "1.4.6": {
                "level": "AAA",
                "title": "Contrast (Enhanced)",
                "description": "The visual presentation of text and images of text has a contrast ratio of at least 7:1."
            },
            "1.4.7": {
                "level": "AAA",
                "title": "Low or No Background Audio",
                "description": "For prerecorded audio-only content that contains primarily speech in the foreground."
            },
            "1.4.8": {
                "level": "AAA",
                "title": "Visual Presentation",
                "description": "For the visual presentation of blocks of text."
            },
            "1.4.9": {
                "level": "AAA",
                "title": "Images of Text (No Exception)",
                "description": "Images of text are only used for pure decoration or where a particular presentation of text is essential to the information being conveyed."
            },
            "1.4.10": {
                "level": "AA",
                "title": "Reflow",
                "description": "Content can be presented without loss of information or functionality, and without requiring scrolling in two dimensions."
            },
            "1.4.11": {
                "level": "AA",
                "title": "Non-text Contrast",
                "description": "The visual presentation of user interface components and graphical objects has a contrast ratio of at least 3:1."
            },
            "1.4.12": {
                "level": "AA",
                "title": "Text Spacing",
                "description": "No loss of content or functionality occurs when text spacing is adjusted."
            },
            "1.4.13": {
                "level": "AA",
                "title": "Content on Hover or Focus",
                "description": "Where receiving and then removing pointer hover or keyboard focus triggers additional content to become visible and then hidden."
            }
        }
    },
    "Operable": {
        "2.1 Keyboard Accessible": {
            "2.1.1": {
                "level": "A",
                "title": "Keyboard",
                "description": "All functionality is available from a keyboard."
            },
            "2.1.2": {
                "level": "A",
                "title": "No Keyboard Trap",
                "description": "Keyboard focus can be moved away from a component using only a keyboard."
            },
            "2.1.3": {
                "level": "AAA",
                "title": "Keyboard (No Exception)",
                "description": "All functionality is available from a keyboard without requiring specific timings for individual keystrokes."
            },
            "2.1.4": {
                "level": "A",
                "title": "Character Key Shortcuts",
                "description": "If a keyboard shortcut uses printable character keys, then the shortcut can be turned off, remapped, or will only activate when an associated interface component or button has focus."
            }
        },
        "2.2 Enough Time": {
            "2.2.1": {
                "level": "A",
                "title": "Timing Adjustable",
                "description": "Users are warned of time limits and given options to extend them."
            },
            "2.2.2": {
                "level": "A",
                "title": "Pause, Stop, Hide",
                "description": "Users can pause, stop, or hide moving, blinking, or auto-updating content."
            },
            "2.2.3": {
                "level": "AAA",
                "title": "No Timing",
                "description": "Timing is not an essential part of the event or activity presented by the content."
            },
            "2.2.4": {
                "level": "AAA",
                "title": "Interruptions",
                "description": "Interruptions can be postponed or suppressed by the user."
            },
            "2.2.5": {
                "level": "AAA",
                "title": "Re-authenticating",
                "description": "When an authenticated session expires, the user can continue the activity without loss of data after re-authenticating."
            },
            "2.2.6": {
                "level": "AAA",
                "title": "Timeouts",
                "description": "Users are warned of the duration of any user inactivity that could cause data loss."
            }
        },
        "2.3 Seizures and Physical Reactions": {
            "2.3.1": {
                "level": "A",
                "title": "Three Flashes or Below Threshold",
                "description": "No content flashes more than three times per second."
            },
            "2.3.2": {
                "level": "AAA",
                "title": "Three Flashes",
                "description": "No content flashes more than three times per second."
            },
            "2.3.3": {
                "level": "AAA",
                "title": "Animation from Interactions",
                "description": "Motion animation triggered by interaction can be disabled."
            }
        },
        "2.4 Navigable": {
            "2.4.1": {
                "level": "A",
                "title": "Bypass Blocks",
                "description": "A mechanism is available to bypass blocks of content that are repeated on multiple pages."
            },
            "2.4.2": {
                "level": "A",
                "title": "Page Titled",
                "description": "Web pages have titles that describe topic or purpose."
            },
            "2.4.3": {
                "level": "A",
                "title": "Focus Order",
                "description": "Focus order preserves meaning and operability."
            },
            "2.4.4": {
                "level": "A",
                "title": "Link Purpose (In Context)",
                "description": "The purpose of each link can be determined from the link text or context."
            },
            "2.4.5": {
                "level": "AA",
                "title": "Multiple Ways",
                "description": "More than one way is available to locate a Web page."
            },
            "2.4.6": {
                "level": "AA",
                "title": "Headings and Labels",
                "description": "Headings and labels describe topic or purpose."
            },
            "2.4.7": {
                "level": "AA",
                "title": "Focus Visible",
                "description": "Any keyboard operable user interface has a mode of operation where the keyboard focus indicator is visible."
            },
            "2.4.8": {
                "level": "AAA",
                "title": "Location",
                "description": "Information about the user's location within a set of Web pages is available."
            },
            "2.4.9": {
                "level": "AAA",
                "title": "Link Purpose (Link Only)",
                "description": "A mechanism is available to allow the purpose of each link to be identified from link text alone."
            },
            "2.4.10": {
                "level": "AAA",
                "title": "Section Headings",
                "description": "Section headings are used to organize the content."
            }
        },
        "2.5 Input Modalities": {
            "2.5.1": {
                "level": "A",
                "title": "Pointer Gestures",
                "description": "All functionality that uses multipoint or path-based gestures can be operated with a single pointer."
            },
            "2.5.2": {
                "level": "A",
                "title": "Pointer Cancellation",
                "description": "For functionality that can be operated using a single pointer, at least one of the following is true."
            },
            "2.5.3": {
                "level": "A",
                "title": "Label in Name",
                "description": "For user interface components with labels that include text or images of text, the name contains the text that is presented visually."
            },
            "2.5.4": {
                "level": "A",
                "title": "Motion Actuation",
                "description": "Functionality that can be operated by device motion or user motion can also be operated by user interface components."
            },
            "2.5.5": {
                "level": "AAA",
                "title": "Target Size",
                "description": "The size of the target for pointer inputs is at least 44 by 44 CSS pixels."
            },
            "2.5.6": {
                "level": "AAA",
                "title": "Concurrent Input Mechanisms",
                "description": "Web content does not restrict use of input modalities available on a platform."
            }
        }
    },
    "Understandable": {
        "3.1 Readable": {
            "3.1.1": {
                "level": "A",
                "title": "Language of Page",
                "description": "The default human language of each Web page can be programmatically determined."
            },
            "3.1.2": {
                "level": "AA",
                "title": "Language of Parts",
                "description": "The human language of each passage or phrase can be programmatically determined."
            },
            "3.1.3": {
                "level": "AAA",
                "title": "Unusual Words",
                "description": "A mechanism is available for identifying specific definitions of words or phrases used in an unusual or restricted way."
            },
            "3.1.4": {
                "level": "AAA",
                "title": "Abbreviations",
                "description": "A mechanism for identifying the expanded form or meaning of abbreviations is available."
            },
            "3.1.5": {
                "level": "AAA",
                "title": "Reading Level",
                "description": "When text requires reading ability more advanced than the lower secondary education level, supplemental content is available."
            },
            "3.1.6": {
                "level": "AAA",
                "title": "Pronunciation",
                "description": "A mechanism is available for identifying specific pronunciation of words."
            }
        },
        "3.2 Predictable": {
            "3.2.1": {
                "level": "A",
                "title": "On Focus",
                "description": "When any user interface component receives focus, it does not initiate a change of context."
            },
            "3.2.2": {
                "level": "A",
                "title": "On Input",
                "description": "Changing the setting of any user interface component does not automatically cause a change of context."
            },
            "3.2.3": {
                "level": "AA",
                "title": "Consistent Navigation",
                "description": "Navigational mechanisms that are repeated on multiple pages occur in the same relative order each time they are repeated."
            },
            "3.2.4": {
                "level": "AA",
                "title": "Consistent Identification",
                "description": "Components that have the same functionality within a set of Web pages are identified consistently."
            },
            "3.2.5": {
                "level": "AAA",
                "title": "Change on Request",
                "description": "Changes of context are initiated only by user request or a mechanism is available to turn off such changes."
            }
        },
        "3.3 Input Assistance": {
            "3.3.1": {
                "level": "A",
                "title": "Error Identification",
                "description": "If an input error is automatically detected, the item that is in error is identified and the error is described to the user in text."
            },
            "3.3.2": {
                "level": "A",
                "title": "Labels or Instructions",
                "description": "Labels or instructions are provided when content requires user input."
            },
            "3.3.3": {
                "level": "AA",
                "title": "Error Suggestion",
                "description": "If an input error is automatically detected and suggestions for correction are known, then the suggestions are provided to the user."
            },
            "3.3.4": {
                "level": "AA",
                "title": "Error Prevention (Legal, Financial, Data)",
                "description": "For Web pages that cause legal commitments or financial transactions, that modify or delete user-controllable data, or that submit user test responses."
            },
            "3.3.5": {
                "level": "AAA",
                "title": "Help",
                "description": "Context-sensitive help is available."
            },
            "3.3.6": {
                "level": "AAA",
                "title": "Error Prevention (All)",
                "description": "For Web pages that require the user to submit information, at least one of the following is true."
            }
        }
    },
    "Robust": {
        "4.1 Compatible": {
            "4.1.1": {
                "level": "A",
                "title": "Parsing",
                "description": "In content implemented using markup languages, elements have complete start and end tags, elements are nested according to their specifications, elements do not contain duplicate attributes, and any IDs are unique."
            },
            "4.1.2": {
                "level": "A",
                "title": "Name, Role, Value",
                "description": "For all user interface components, the name and role can be programmatically determined; states, properties, and values can be programmatically set; and notification of changes to these items is available to user agents."
            },
            "4.1.3": {
                "level": "AA",
                "title": "Status Messages",
                "description": "In content implemented using markup languages, status messages can be programmatically determined through role or properties such that they can be presented to the user by assistive technologies without receiving focus."
            }
        }
    }
}