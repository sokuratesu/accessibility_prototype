"""
Visual Diff Tool for comparing screenshots from different browsers.
"""

import os
import logging
from typing import List, Tuple, Dict, Optional
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont
import cv2


class VisualDiffTool:
    """Tool for comparing screenshots visually."""

    def __init__(self):
        """Initialize the visual diff tool."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def compare_screenshots(self, screenshot1_path: str, screenshot2_path: str, output_path: str) -> Dict:
        """Compare two screenshots and highlight differences.

        Args:
            screenshot1_path (str): Path to first screenshot
            screenshot2_path (str): Path to second screenshot
            output_path (str): Path to save diff image

        Returns:
            dict: Comparison results
        """
        try:
            # Open images
            img1 = Image.open(screenshot1_path)
            img2 = Image.open(screenshot2_path)

            # Resize images to the same size if needed
            if img1.size != img2.size:
                # Resize the smaller image to match the larger one
                if img1.size[0] * img1.size[1] > img2.size[0] * img2.size[1]:
                    img2 = img2.resize(img1.size)
                else:
                    img1 = img1.resize(img2.size)

            # Compute difference
            diff = ImageChops.difference(img1, img2)

            # Convert to cv2 format for better analysis
            diff_cv = np.array(diff)

            # Convert to grayscale
            if len(diff_cv.shape) == 3:
                diff_gray = cv2.cvtColor(diff_cv, cv2.COLOR_RGB2GRAY)
            else:
                diff_gray = diff_cv

            # Apply threshold
            _, thresh = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)

            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filter out small contours
            significant_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]

            # Create a mask for the differences
            mask = np.zeros_like(diff_gray)
            cv2.drawContours(mask, significant_contours, -1, 255, -1)

            # Create a colored diff image
            diff_highlight = np.array(img1)
            diff_highlight[mask > 0] = [255, 0, 0]  # Red highlight

            # Create a side-by-side comparison
            width = img1.width + img2.width + diff_highlight.shape[1]
            height = max(img1.height, img2.height, diff_highlight.shape[0])

            comparison = Image.new('RGB', (width, height))

            # Paste images
            comparison.paste(img1, (0, 0))
            comparison.paste(img2, (img1.width, 0))
            comparison.paste(Image.fromarray(diff_highlight), (img1.width + img2.width, 0))

            # Add labels
            draw = ImageDraw.Draw(comparison)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()

            draw.text((10, 10), "Image 1", fill="white", stroke_fill="black", stroke_width=2, font=font)
            draw.text((img1.width + 10, 10), "Image 2", fill="white", stroke_fill="black", stroke_width=2, font=font)
            draw.text((img1.width + img2.width + 10, 10), "Differences", fill="white", stroke_fill="black",
                      stroke_width=2, font=font)

            # Save comparison
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            comparison.save(output_path)

            # Calculate difference metrics
            diff_percentage = (np.sum(mask > 0) / mask.size) * 100
            diff_pixels = np.sum(mask > 0)
            diff_regions = len(significant_contours)

            # Return results
            return {
                "diff_percentage": diff_percentage,
                "diff_pixels": diff_pixels,
                "diff_regions": diff_regions,
                "diff_image_path": output_path,
                "has_differences": diff_regions > 0
            }

        except Exception as e:
            self.logger.error(f"Error comparing screenshots: {str(e)}")
            return {
                "error": str(e),
                "has_differences": None
            }

    def compare_multiple_screenshots(self, screenshots: List[str], output_dir: str,
                                     base_screenshot: Optional[str] = None) -> Dict:
        """Compare multiple screenshots.

        Args:
            screenshots (list): List of screenshot paths
            output_dir (str): Directory to save diff images
            base_screenshot (str, optional): Base screenshot to compare against. If None, use first screenshot.

        Returns:
            dict: Comparison results
        """
        if not screenshots:
            return {"error": "No screenshots provided"}

        try:
            os.makedirs(output_dir, exist_ok=True)

            # Use specified base or first screenshot as reference
            base = base_screenshot if base_screenshot else screenshots[0]

            results = {}

            for i, screenshot in enumerate(screenshots):
                if screenshot == base:
                    continue

                filename1 = os.path.basename(base)
                filename2 = os.path.basename(screenshot)

                output_filename = f"diff_{filename1.split('.')[0]}_{filename2.split('.')[0]}.png"
                output_path = os.path.join(output_dir, output_filename)

                result = self.compare_screenshots(base, screenshot, output_path)
                results[filename2] = result

            return results

        except Exception as e:
            self.logger.error(f"Error comparing multiple screenshots: {str(e)}")
            return {"error": str(e)}

    def batch_compare_browser_screenshots(self, screenshot_dirs: Dict[str, str], output_dir: str,
                                          reference_browser: Optional[str] = None) -> Dict:
        """Compare screenshots across browsers.

        Args:
            screenshot_dirs (dict): Dictionary mapping browser names to screenshot directories
            output_dir (str): Directory to save diff images
            reference_browser (str, optional): Reference browser for comparison. If None, use first browser.

        Returns:
            dict: Comparison results
        """
        if not screenshot_dirs:
            return {"error": "No screenshot directories provided"}

        try:
            os.makedirs(output_dir, exist_ok=True)

            browsers = list(screenshot_dirs.keys())

            # Use specified reference browser or first browser
            ref_browser = reference_browser if reference_browser in browsers else browsers[0]
            ref_dir = screenshot_dirs[ref_browser]

            # Get all screenshots from reference browser
            ref_screenshots = []
            for root, _, files in os.walk(ref_dir):
                for file in files:
                    if file.endswith(('.png', '.jpg', '.jpeg')):
                        ref_screenshots.append(os.path.join(root, file))

            results = {
                "reference_browser": ref_browser,
                "comparisons": {}
            }

            # Compare each reference screenshot with corresponding screenshots from other browsers
            for ref_screenshot in ref_screenshots:
                screenshot_name = os.path.basename(ref_screenshot)
                results["comparisons"][screenshot_name] = {}

                for browser, screenshot_dir in screenshot_dirs.items():
                    if browser == ref_browser:
                        continue

                    # Find corresponding screenshot in this browser
                    browser_screenshots = []
                    for root, _, files in os.walk(screenshot_dir):
                        for file in files:
                            if file == screenshot_name:
                                browser_screenshots.append(os.path.join(root, file))

                    if not browser_screenshots:
                        results["comparisons"][screenshot_name][browser] = {
                            "error": f"No matching screenshot found for {browser}"
                        }
                        continue

                    # Compare screenshots
                    output_path = os.path.join(output_dir, f"diff_{ref_browser}_{browser}_{screenshot_name}")
                    result = self.compare_screenshots(ref_screenshot, browser_screenshots[0], output_path)
                    results["comparisons"][screenshot_name][browser] = result

            return results

        except Exception as e:
            self.logger.error(f"Error in batch comparison: {str(e)}")
            return {"error": str(e)}