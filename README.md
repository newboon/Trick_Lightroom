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

## Disclaimer

This tool is created purely for experimental and entertainment purposes. The results may vary significantly from actual camera profiles.

---

# Trick Lightroom (한국어)

RAW 파일의 EXIF 정보를 변경하여 다른 카메라의 프로필을 실험해볼 수 있는 유틸리티입니다.

## 개요

Trick Lightroom은 RAW 파일의 카메라 식별 정보를 수정하여 라이트룸에서 다른 카메라의 프로필을 적용해볼 수 있게 해주는 도구입니다. 예를 들어, 소니 카메라로 촬영한 RAW 파일을 후지필름 카메라로 촬영한 것처럼 인식하게 할 수 있습니다.

**참고**: 이 도구는 순전히 재미를 위한 것입니다! 예를 들어 소니 RAW 파일에 후지필름 프로필을 적용한 결과물은 실제 후지필름 카메라의 RAW 파일에 동일한 프로필을 적용한 결과와는 당연히 다릅니다.

## 사용 방법

![스크린샷](/.github/screenshot.png)

1. [Adobe 공식 웹사이트](https://helpx.adobe.com/kr/camera-raw/using/adobe-dng-converter.html)에서 Adobe DNG Converter를 다운로드하고 설치합니다
2. [GitHub Releases](https://github.com/newboon/Trick_Lightroom/releases)에서 Trick Lightroom을 다운로드하고 실행합니다
3. RAW 파일을 좌측 패널에 드래그 앤 드롭합니다 (예: DSC1000.ARW)
4. 변환 버튼을 클릭하면 EXIF 정보가 변경된 DNG 파일이 생성됩니다 (예: DSC1000_GFX100.DNG)
5. 생성된 DNG 파일을 라이트룸으로 불러와서 편집한 후 JPG 파일로 내보냅니다 (예: DSC1000_GFX100.JPG)
6. 내보낸 JPG 파일을 우측 패널에 드래그 앤 드롭하고 복원 버튼을 클릭하면 원래 카메라의 EXIF 정보로 되돌아갑니다

## 요구사항

- Windows OS
- Adobe DNG Converter

## 면책사항

이 도구는 순전히 실험적이고 재미를 위한 목적으로 제작되었습니다. 실제 카메라 프로필과는 상당히 다른 결과가 나올 수 있습니다.
