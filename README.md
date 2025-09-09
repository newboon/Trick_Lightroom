# Trick Lightroom

A fun utility that tricks Adobe Lightroom by modifying RAW file EXIF data to experiment with different camera profiles.

## Overview

Trick Lightroom allows you to modify the camera identification in RAW files so you can apply different camera profiles in Lightroom. For example, you can make a Sony RAW file appear as if it was shot on a Fujifilm camera.

**Note**: This is just for fun! The results when applying a Fujifilm profile to a Sony RAW file will naturally differ from applying the same profile to an actual Fujifilm RAW file.

## How to Use

![Screenshot](/.github/screenshot.png)

1. Download and install Adobe DNG Converter from [Adobe's official website](https://helpx.adobe.com/camera-raw/using/adobe-dng-converter.html)
2. Download and run Trick Lightroom from [GitHub Releases](https://github.com/yourusername/Trick_Lightroom/releases)
3. Drop your RAW files into the left panel (e.g., DSC1000.ARW)
4. Click the convert button to generate DNG files with modified EXIF data (e.g., DSC1000_GFX100.DNG)  
5. Import the generated DNG files into Lightroom, edit, and export as JPG (e.g., DSC1000_GFX100.JPG)
6. Drop the exported JPG files into the right panel and click restore to revert EXIF data to the original camera

## Requirements

- Windows OS
- Adobe DNG Converter
- Adobe Lightroom

## Disclaimer

This tool is created purely for experimental and entertainment purposes. The results may vary significantly from actual camera profiles.
