# Trick Lightroom

A fun utility that tricks Adobe Lightroom by modifying RAW file EXIF data to experiment with different camera profiles.

## Overview

Trick Lightroom allows you to modify the camera identification in RAW files so you can apply different camera profiles in Lightroom. For example, you can make a Sony RAW file appear as if it was shot on a Fujifilm camera.

**Note**: This is just for fun! The results when applying a Fujifilm profile to a Sony RAW file will naturally differ from applying the same profile to an actual Fujifilm RAW file.

## How to Use

![Screenshot](/.github/screenshot.png)

1. Download and install Adobe DNG Converter from [Adobe's official website](https://helpx.adobe.com/camera-raw/using/adobe-dng-converter.html)
2. Download and run Trick Lightroom from [GitHub Releases](https://github.com/yourusername/Trick_Lightroom/releases)

   For macOS version, visit here: https://github.com/dcbfs/Trick_Lightroom_Mac
3. Drop your RAW files into the left panel (e.g., DSC1000.ARW)
4. Click the convert button to generate DNG files with modified EXIF data (e.g., DSC1000_GFX100.DNG)  
5. Import the generated DNG files into Lightroom, edit, and export as JPG (e.g., DSC1000_GFX100.JPG)
6. Drop the exported JPG files into the right panel and click restore to revert EXIF data to the original camera

For example, when you change the EXIF information to Fujifilm, Ricoh, or Panasonic cameras, you can use their Lightroom profiles as shown below:

<div style="display: flex; justify-content: space-between;">
    <img src="/.github/fuji.png" width="32%" alt="Fujifilm Profile">
    <img src="/.github/ricoh.png" width="32%" alt="Ricoh Profile">
    <img src="/.github/panasonic.png" width="32%" alt="Panasonic Profile">
</div>

## Requirements

- Windows OS
- Adobe DNG Converter

## Disclaimer

This tool is created purely for experimental and entertainment purposes. The results may vary significantly from actual camera profiles.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the [LICENSE](LICENSE) file for details.

This project uses the following open source software:

### ExifTool
- Author: Phil Harvey
- License: Perl Artistic License
- Website: https://exiftool.org/
- License Details: https://exiftool.org/#license

ExifTool is used for reading and writing EXIF metadata in image files. It is available under the Perl Artistic License.

### PySide6 (Qt for Python)
- Author: Qt Company
- License: LGPL v3.0
- Website: https://www.qt.io/qt-for-python
- License Details: https://doc.qt.io/qtforpython-6/licenses.html

PySide6 is used for the graphical user interface. It is available under the LGPL v3.0 license.

---

# Trick Lightroom (한국어)

RAW 파일의 EXIF 정보를 변경하여 다른 카메라의 프로필을 실험해볼 수 있는 유틸리티입니다.

## 개요

Trick Lightroom은 RAW 파일의 카메라 EXIF 정보를 수정하여 라이트룸에서 다른 카메라의 프로필을 적용해볼 수 있게 해주는 도구입니다. 예를 들어, 소니 카메라로 촬영한 RAW 파일을 후지필름 카메라로 촬영한 것처럼 인식하게 할 수 있습니다.

**참고**: 이 도구는 순전히 재미를 위한 것입니다! 예를 들어 소니 RAW 파일에 후지필름 프로필을 적용한 결과물은 실제 후지필름 카메라의 RAW 파일에 동일한 프로필을 적용한 결과와는 당연히 다릅니다.

## 사용 방법

![스크린샷](/.github/screenshot.png)

1. [Adobe 공식 웹사이트](https://helpx.adobe.com/kr/camera-raw/using/adobe-dng-converter.html)에서 Adobe DNG Converter를 다운로드하고 설치합니다
2. [GitHub Releases](https://github.com/newboon/Trick_Lightroom/releases)에서 Trick Lightroom을 다운로드하고 실행합니다

   macOS 버전은 여기로 가세요: https://github.com/dcbfs/Trick_Lightroom_Mac
3. RAW 파일을 좌측 패널에 드래그 앤 드롭합니다 (예: DSC1000.ARW)
4. 변환 버튼을 클릭하면 EXIF 정보가 변경된 DNG 파일이 생성됩니다 (예: DSC1000_GFX100.DNG)
5. 생성된 DNG 파일을 라이트룸으로 불러와서 편집한 후 JPG 파일로 내보냅니다 (예: DSC1000_GFX100.JPG)
6. 내보낸 JPG 파일을 우측 패널에 드래그 앤 드롭하고 복원 버튼을 클릭하면 원래 카메라의 EXIF 정보로 되돌아갑니다

예를 들어 후지, 리코, 파나소닉 카메라로 EXIF 정보를 변경하면 각각 아래처럼 라이트룸 프로필을 사용할 수 있습니다:

<div style="display: flex; justify-content: space-between;">
    <img src="/.github/fuji.png" width="32%" alt="후지필름 프로필">
    <img src="/.github/ricoh.png" width="32%" alt="리코 프로필">
    <img src="/.github/panasonic.png" width="32%" alt="파나소닉 프로필">
</div>

## 요구사항

- Windows OS
- Adobe DNG Converter

## 면책사항

이 도구는 순전히 실험적이고 재미를 위한 목적으로 제작되었습니다. 실제 카메라 프로필과는 상당히 다른 결과가 나올 수 있습니다.

## 라이선스

이 프로젝트는 GNU Affero General Public License v3.0 (AGPL-3.0) 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

이 프로젝트는 다음과 같은 오픈소스 소프트웨어를 사용합니다:

### ExifTool
- 제작자: Phil Harvey
- 라이선스: Perl Artistic License
- 웹사이트: https://exiftool.org/
- 라이선스 세부정보: https://exiftool.org/#license

ExifTool은 이미지 파일의 EXIF 메타데이터를 읽고 쓰는 데 사용됩니다. Perl Artistic License 하에 제공됩니다.

### PySide6 (Qt for Python)
- 제작자: Qt Company
- 라이선스: LGPL v3.0
- 웹사이트: https://www.qt.io/qt-for-python
- 라이선스 세부정보: https://doc.qt.io/qtforpython-6/licenses.html

PySide6는 그래픽 사용자 인터페이스를 위해 사용됩니다. LGPL v3.0 라이선스 하에 제공됩니다.
