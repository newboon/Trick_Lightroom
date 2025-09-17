import sys
import ctypes
import os
import subprocess
import json
import re
from pathlib import Path
import traceback
import shutil

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QGroupBox, QCheckBox, QFrame, QMenu
)
from PySide6.QtCore import Qt, QSettings, QThread, Signal, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDesktopServices

# --- 상수 정의 ---
APP_NAME = "Trick Lightroom"

# 다국어 텍스트 (요청사항 반영)
LANGUAGES = {
    "en": {
        "window_title": f"{APP_NAME}",
        "dng_converter_path": "Adobe DNG Converter Path:",
        "browse": "Browse...",
        "lang_select": "Language",
        "raw_to_dng_group": "1. RAW to DNG && EXIF Modification(Original files will be preserved)",
        "drop_raw_files": "Drop RAW files here",
        "jpg_restore_group": "2. Restore EXIF for JPG",
        "drop_jpg_files": "Drop JPG files here",
        "open_file": "Open File",
        "open_folder": "Open Containing Folder",
        "col_status": "Status",
        "add": "Add...",
        "remove": "Remove",
        "clear": "Clear",
        "target_camera": "Target Camera:",
        "output_folder": "Output Folder:",
        "same_as_source": "Same as source folder",
        "select_folder": "Select folder...",
        "convert_button": "Convert to DNG && Modify EXIF",
        "remove_camera_name": "Remove camera name from filename (e.g., _XT5)",
        "restore_button": "Restore Original Camera EXIF",
        "col_filename": "Filename",
        "col_path": "Path",
        "col_model": "Model",
        "col_status": "Status",
        "dng_converter_found": "Adobe DNG Converter found. You can now use Trick Lightroom.",
        "dng_converter_not_found": "Adobe DNG Converter not found. Please set the path manually.",
        "conversion_complete": "Conversion Complete",
        "files_processed_successfully": "files processed successfully.",
        "exif_restore_complete": "EXIF Restore Complete",
        "error": "Error",
        "processing": "Processing...",
        "ready": "Ready",
        "select_camera_msg": "Please select at least one target camera.",
        "output_folder_not_exist_msg": "The specified output folder does not exist.",
        "select_output_folder_msg": "Please select an output folder first.",
    },
    "ko": {
        "window_title": f"{APP_NAME}",
        "dng_converter_path": "Adobe DNG Converter 경로:",
        "browse": "찾아보기...",
        "lang_select": "언어",
        "raw_to_dng_group": "1. DNG 변환 및 EXIF 수정(원본 파일은 그대로 유지됩니다)",
        "drop_raw_files": "이곳에 RAW 파일을 드롭하세요",
        "jpg_restore_group": "2. JPG EXIF 정보 복원",
        "drop_jpg_files": "이곳에 JPG 파일을 드롭하세요",
        "open_file": "파일 열기",
        "open_folder": "경로 열기",
        "col_status": "작업 완료",
        "add": "추가...",
        "remove": "삭제",
        "clear": "비우기",
        "target_camera": "변경할 카메라:",
        "output_folder": "저장 폴더:",
        "same_as_source": "원본 사진과 동일한 폴더",
        "select_folder": "폴더 지정...",
        "convert_button": "DNG 변환 및 EXIF 정보 수정",
        "remove_camera_name": "파일명에서 카메라 이름 지우기 (예: _XT5)",
        "restore_button": "원래 카메라의 EXIF 정보로 복원",
        "col_filename": "파일명",
        "col_path": "경로",
        "col_model": "기종",
        "col_status": "작업 완료",
        "dng_converter_found": "Adobe DNG Converter를 찾았습니다. Trick Lightroom을 사용할 수 있습니다.",
        "dng_converter_not_found": "Adobe DNG Converter를 찾을 수 없습니다. 경로를 직접 지정해주세요.",
        "conversion_complete": "변환 완료",
        "files_processed_successfully": "개의 파일 처리가 완료되었습니다.",
        "exif_restore_complete": "EXIF 복원 완료",
        "error": "오류",
        "processing": "처리 중...",
        "ready": "준비됨",
        "select_camera_msg": "하나 이상의 카메라를 선택해주세요.",
        "output_folder_not_exist_msg": "지정된 저장 폴더가 존재하지 않습니다.",
        "select_output_folder_msg": "먼저 저장 폴더를 지정해주세요.",
    }
}

# 카메라 정보
CAMERA_DATA = { 
    "Canon EOS R5 Mark II": {"make": "Canon", "model": "Canon EOS R5m2", "unique": "Canon EOS R5 Mark II", "suffix": "R5M2"}, 
    "Nikon Z8": {"make": "NIKON CORPORATION", "model": "NIKON Z 8", "unique": "Nikon Z 8", "suffix": "Z8"}, 
    "Sony RX1R3": {"make": "SONY", "model": "DSC-RX1RM3", "unique": "Sony DSC-RX1RM3", "suffix": "RX1R3"}, 
    "Fujifilm GFX100RF (Bayer Sensor)": {"make": "FUJIFILM", "model": "GFX100RF", "unique": "Fujifilm GFX 100RF", "suffix": "GFX100RF"}, 
    "Fujifilm X-T5 (X-Trans Sensor)": {"make": "FUJIFILM", "model": "X-T5", "unique": "Fujifilm X-T5", "suffix": "XT5"}, 
    "Panasonic LUMIX DC-S9": {"make": "Panasonic", "model": "DC-S9", "unique": "Panasonic DC-S9", "suffix": "S9"}, 
    "Ricoh GR IV": {"make": "RICOH IMAGING COMPANY, LTD.", "model": "RICOH GR IV", "unique": "RICOH GR IV", "suffix": "GR4"}, 
    "OM Digital OM-3": {"make": "OM Digital Solutions", "model": "OM-3", "unique": "OM Digital Solutions OM-3", "suffix": "OM3"}, 
    }

# --- 작업자 스레드 ---
class Worker(QThread):
    progress = Signal(str)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, mode, files, options, exiftool_path):
        super().__init__()
        self.mode = mode
        self.files = list(files) # 원본 경로 형식 유지
        self.options = options
        self.exiftool_path = exiftool_path
        if not os.path.exists(self.exiftool_path):
            self.exiftool_path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), 'exiftool.exe')

    def run(self):
        try:
            if self.mode == 'convert':
                self.run_conversion()
            elif self.mode == 'restore':
                self.run_restore()
        except Exception as e:
            error_message = f"An unexpected error occurred in the worker thread:\n\n{traceback.format_exc()}"
            self.error.emit(error_message)

    def run_command(self, command_list):
        try:
            process = subprocess.run(command_list, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
            return process.stdout
        except FileNotFoundError:
            self.error.emit(f"Command not found: {command_list[0]}")
            return None
        except subprocess.CalledProcessError as e:
            self.error.emit(f"Command failed: {' '.join(command_list)}\nError: {e.stderr}")
            return None

    def run_conversion(self):
        dng_converter_path = self.options['dng_path']
        target_cameras_keys = self.options['target_cameras']
        output_path = self.options['output_path']
        successful_files = []

        for i, file_path in enumerate(self.files):
            self.progress.emit(f"Processing ({i+1}/{len(self.files)}): {os.path.basename(file_path)}")
            
            # 1. DNG 변환 (소스 파일 당 한 번만 실행)
            normalized_file_path = os.path.normpath(file_path)
            dng_command_list = [dng_converter_path, "-d", output_path, normalized_file_path]
            self.run_command(dng_command_list)
            
            base_name, _ = os.path.splitext(os.path.basename(file_path))
            temp_dng_path = os.path.join(output_path, f"{base_name}.dng")

            if not os.path.exists(temp_dng_path):
                self.progress.emit(f"Failed to convert {os.path.basename(file_path)} to DNG.")
                continue

            any_conversion_succeeded = False
            try:
                # 2. 선택된 각 카메라에 대해 DNG 파일 복사, EXIF 수정, 이름 변경 작업 반복
                for target_camera_key in target_cameras_keys:
                    target_camera = CAMERA_DATA[target_camera_key]
                    
                    final_filename = f"{base_name}_{target_camera['suffix']}.dng"
                    final_filepath = os.path.join(output_path, final_filename)

                    shutil.copy2(temp_dng_path, final_filepath)

                    exif_command_list = [self.exiftool_path, "-overwrite_original", f'-Make={target_camera["make"]}', f'-Model={target_camera["model"]}', f'-UniqueCameraModel={target_camera["unique"]}', final_filepath]
                    self.run_command(exif_command_list)
                    any_conversion_succeeded = True

            finally:
                # 3. 모든 작업 완료 후 임시 DNG 파일 삭제
                if os.path.exists(temp_dng_path):
                    os.remove(temp_dng_path)

            if any_conversion_succeeded:
                successful_files.append(file_path)

        self.finished.emit(successful_files)


    def run_restore(self):
        original_exif_data = self.options['original_exif_data']
        remove_suffix = self.options['remove_suffix']
        successful_files = []
        for i, file_path in enumerate(self.files): # file_path는 원본 경로 형식
            self.progress.emit(f"Restoring ({i+1}/{len(self.files)}): {os.path.basename(file_path)}")
            base_name = os.path.basename(file_path)
            original_base_name = re.sub(r'_[A-Z0-9]+$', '', os.path.splitext(base_name)[0])
            if original_base_name in original_exif_data:
                original_info = original_exif_data[original_base_name]
                make = original_info.get("make", "")
                model = original_info.get("model", "")
                unique_model = original_info.get("unique", f"{make} {model}")
                
                # 외부 프로그램 호출 직전에만 경로를 OS 표준 형식으로 변환
                normalized_file_path = os.path.normpath(file_path)
                exif_command_list = [self.exiftool_path, "-overwrite_original", f'-Make={make}', f'-Model={model}', f'-UniqueCameraModel={unique_model}', normalized_file_path]
                
                self.run_command(exif_command_list)
                if remove_suffix:
                    new_filename = f"{original_base_name}{os.path.splitext(file_path)[1]}"
                    new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
                    if file_path != new_file_path:
                        try: os.rename(file_path, new_file_path)
                        except OSError as e: self.progress.emit(f"Failed to rename {base_name}: {e}")
                successful_files.append(file_path) # 성공 리스트에는 원본 경로를 추가
            else:
                self.progress.emit(f"Original EXIF not found for {base_name}")
        self.finished.emit(successful_files)


# --- 드래그앤드롭 테이블 위젯 ---
class DragDropTableWidget(QTableWidget):
    filesDropped = Signal(list)

    def __init__(self, texts, parent=None, allowed_extensions=None):
        super().__init__(parent)
        self.texts = texts # 컨텍스트 메뉴 번역을 위해 texts 딕셔너리 받기
        self.setAcceptDrops(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setAlternatingRowColors(True)
        if allowed_extensions is not None:
            self.allowed_extensions = {ext.lower() for ext in allowed_extensions}
        else:
            self.allowed_extensions = None

    def set_headers(self, headers):
        column_count = len(headers)
        self.setColumnCount(column_count)
        self.setHorizontalHeaderLabels(headers)
        header = self.horizontalHeader()

        # 현재 헤더 구성: ['파일명', '기종', '작업 완료'] (3개 열)
        if column_count == 3:
            # 0번 열 ('파일명')은 내용에 맞게 크기 조절
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            
            # 1번 열 ('기종')은 남은 공간을 모두 채우도록 설정
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            
            # 2번 열 ('작업 완료')은 내용에 맞게 크기 조절
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        else:
            # 예외적인 경우 (헤더 개수가 다를 때) 마지막 열만 늘어나도록 안전장치 설정
            header.setStretchLastSection(True)

    # --- 우클릭 컨텍스트 메뉴 이벤트 핸들러 ---
    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if not item:
            return

        # 0번 열(파일명) 아이템에서 숨겨진 전체 경로 데이터를 가져옴
        full_path = self.item(item.row(), 0).data(Qt.UserRole)
        if not full_path:
            return
        
        menu = QMenu(self)
        open_file_action = menu.addAction(self.texts["open_file"])
        open_folder_action = menu.addAction(self.texts["open_folder"])

        action = menu.exec(event.globalPos())

        if action == open_file_action:
            QDesktopServices.openUrl(QUrl.fromLocalFile(full_path))
        elif action == open_folder_action:
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(full_path)))

    # --- 드래그 앤 드롭 이벤트 핸들러 (이전과 동일) ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            all_files_valid = all(os.path.isfile(url.toLocalFile()) and (not self.allowed_extensions or os.path.splitext(url.toLocalFile())[1].lower() in self.allowed_extensions) for url in event.mimeData().urls())
            if all_files_valid: event.acceptProposedAction()
            else: event.ignore()
        else: event.ignore()
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
        else: event.ignore()
    def dropEvent(self, event: QDropEvent):
        file_paths = [url.toLocalFile() for url in event.mimeData().urls() if not self.allowed_extensions or os.path.splitext(url.toLocalFile())[1].lower() in self.allowed_extensions]
        if file_paths: event.acceptProposedAction(); self.filesDropped.emit(file_paths)
        else: event.ignore()

def apply_dark_title_bar(widget):
    """주어진 위젯의 제목 표시줄에 다크 테마를 적용합니다 (Windows 전용)."""
    if sys.platform == "win32":
        try:
            # import ctypes # 함수 안보다는 파일 상단에 두는 것이 일반적입니다.
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            dwmapi = ctypes.WinDLL("dwmapi")
            hwnd = int(widget.winId())
            value = ctypes.c_int(1)
            dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
        except Exception as e:
            # logging 모듈 대신 간단한 print로 변경
            print(f"Failed to apply dark title bar to {type(widget).__name__}: {e}")


# --- 메인 윈도우 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        self.exiftool_path = os.path.join(base_path, 'exiftool', 'exiftool.exe')

        settings_path = "settings.ini"
        self.settings = QSettings(settings_path, QSettings.Format.IniFormat)

        self.current_lang = self.settings.value("language", "en")
        self.texts = LANGUAGES[self.current_lang]
        self.original_exif_data = {}
        self.exif_data_file = "original_exif_data.json"
        
        self.raw_files_paths = []
        self.jpg_files_paths = []

        self.completed_raw_paths = set()
        self.completed_jpg_paths = set()

        self.load_original_exif_data()
        self.init_ui()
        self.load_settings()
        self.check_dng_converter_on_startup()
        apply_dark_title_bar(self)

    def init_ui(self):
        self.setWindowTitle(self.texts["window_title"])
        self.setGeometry(100, 100, 900, 800)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        top_layout = QHBoxLayout()
        columns_layout = QHBoxLayout()
        dng_path_group = QGroupBox(self.texts["dng_converter_path"])
        dng_path_layout = QHBoxLayout(dng_path_group)
        self.dng_path_edit = QLineEdit()
        self.dng_path_edit.setReadOnly(True)
        self.dng_browse_btn = QPushButton(self.texts["browse"])
        self.dng_browse_btn.clicked.connect(self.browse_dng_converter)
        dng_path_layout.addWidget(self.dng_path_edit)
        dng_path_layout.addWidget(self.dng_browse_btn)
        lang_group = QGroupBox(self.texts["lang_select"])
        lang_layout = QHBoxLayout(lang_group)
        self.radio_en = QRadioButton("English")
        self.radio_ko = QRadioButton("한국어")
        self.radio_en.toggled.connect(lambda: self.change_language("en"))
        self.radio_ko.toggled.connect(lambda: self.change_language("ko"))
        lang_layout.addWidget(self.radio_en)
        lang_layout.addWidget(self.radio_ko)
        if self.current_lang == "ko": self.radio_ko.setChecked(True)
        else: self.radio_en.setChecked(True)
        top_layout.addWidget(dng_path_group, 1)
        top_layout.addWidget(lang_group)

        # RAW 파일 섹션 UI 구성
        self.raw_group = QGroupBox(self.texts["raw_to_dng_group"])
        raw_layout = QVBoxLayout(self.raw_group)
        raw_top_bar_layout = QHBoxLayout()
        raw_top_bar_layout.addWidget(QLabel(self.texts["drop_raw_files"]))
        raw_top_bar_layout.addStretch()
        self.add_raw_btn = QPushButton(self.texts["add"])
        self.remove_raw_btn = QPushButton(self.texts["remove"])
        self.clear_raw_btn = QPushButton(self.texts["clear"])
        raw_top_bar_layout.addWidget(self.add_raw_btn)
        raw_top_bar_layout.addWidget(self.remove_raw_btn)
        raw_top_bar_layout.addWidget(self.clear_raw_btn)
        self.add_raw_btn.clicked.connect(self.add_raw_files)
        self.remove_raw_btn.clicked.connect(self.remove_raw_files)
        self.clear_raw_btn.clicked.connect(self.clear_raw_files)
        raw_extensions = {'.arw', '.crw', '.dng', '.cr2', '.cr3', '.nef', '.nrw', '.raf', '.srw', '.srf', '.sr2', '.rw2', '.rwl', '.x3f', '.gpr', '.orf', '.pef', '.ptx', '.3fr', '.fff', '.mef', '.iiq', '.braw', '.ari', '.r3d'}
        self.raw_table_widget = DragDropTableWidget(self.texts, allowed_extensions=raw_extensions)
        self.raw_table_widget.set_headers([self.texts["col_filename"], self.texts["col_model"], self.texts["col_status"]])
        self.raw_table_widget.filesDropped.connect(self.on_raw_files_dropped)
        
        from PySide6.QtWidgets import QScrollArea
        self.camera_checkboxes = []
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(120) # 스크롤 영역의 높이 고정
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)
        for camera_name in CAMERA_DATA.keys():
            checkbox = QCheckBox(camera_name)
            self.camera_checkboxes.append(checkbox)
            checkbox_layout.addWidget(checkbox)
        scroll_area.setWidget(checkbox_container)
        
        self.output_same_radio = QRadioButton(self.texts["same_as_source"])
        self.output_custom_radio = QRadioButton(self.texts["select_folder"])
        self.output_same_radio.setChecked(True)
        custom_folder_layout = QHBoxLayout()
        self.custom_folder_path_label = QLabel("")
        self.custom_folder_path_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.custom_folder_browse_btn = QPushButton(self.texts["browse"])
        self.custom_folder_browse_btn.clicked.connect(self.browse_output_folder)
        custom_folder_layout.addWidget(self.custom_folder_path_label, 1)
        custom_folder_layout.addWidget(self.custom_folder_browse_btn)
        self.convert_button = QPushButton(self.texts["convert_button"])
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setFixedHeight(40)
        raw_layout.addLayout(raw_top_bar_layout)
        raw_layout.addWidget(self.raw_table_widget)
        raw_layout.addWidget(QLabel(self.texts["target_camera"]))
        
        raw_layout.addWidget(scroll_area) # 콤보박스 대신 스크롤 영역 추가

        raw_layout.addWidget(QLabel(self.texts["output_folder"]))
        raw_layout.addWidget(self.output_same_radio)
        raw_layout.addWidget(self.output_custom_radio)
        raw_layout.addLayout(custom_folder_layout)
        raw_layout.addSpacing(20)
        raw_layout.addWidget(self.convert_button)

        # JPG 복원 섹션 UI 구성 (기존 코드와 동일)
        self.jpg_group = QGroupBox(self.texts["jpg_restore_group"])
        jpg_layout = QVBoxLayout(self.jpg_group)
        jpg_top_bar_layout = QHBoxLayout()
        jpg_top_bar_layout.addWidget(QLabel(self.texts["drop_jpg_files"]))
        jpg_top_bar_layout.addStretch()
        self.add_jpg_btn = QPushButton(self.texts["add"])
        self.remove_jpg_btn = QPushButton(self.texts["remove"])
        self.clear_jpg_btn = QPushButton(self.texts["clear"])
        jpg_top_bar_layout.addWidget(self.add_jpg_btn)
        jpg_top_bar_layout.addWidget(self.remove_jpg_btn)
        jpg_top_bar_layout.addWidget(self.clear_jpg_btn)
        self.add_jpg_btn.clicked.connect(self.add_jpg_files)
        self.remove_jpg_btn.clicked.connect(self.remove_jpg_files)
        self.clear_jpg_btn.clicked.connect(self.clear_jpg_files)
        self.jpg_table_widget = DragDropTableWidget(self.texts, allowed_extensions={'.jpg', '.jpeg'})
        self.jpg_table_widget.set_headers([self.texts["col_filename"], self.texts["col_model"], self.texts["col_status"]])
        self.jpg_table_widget.filesDropped.connect(self.on_jpg_files_dropped)
        self.remove_suffix_checkbox = QCheckBox(self.texts["remove_camera_name"])
        self.restore_button = QPushButton(self.texts["restore_button"])
        self.restore_button.clicked.connect(self.start_restore)
        self.restore_button.setFixedHeight(40)
        jpg_layout.addLayout(jpg_top_bar_layout)
        jpg_layout.addWidget(self.jpg_table_widget)
        jpg_layout.addWidget(self.remove_suffix_checkbox)
        jpg_layout.addSpacing(20)
        jpg_layout.addWidget(self.restore_button)
        
        columns_layout.addWidget(self.raw_group)
        columns_layout.addWidget(self.jpg_group)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(columns_layout)
        self.statusBar().showMessage(self.texts["ready"])


    def change_language(self, lang):
        if (self.radio_en.isChecked() and self.current_lang != "en") or (self.radio_ko.isChecked() and self.current_lang != "ko"): self.current_lang = lang
        else: return
        self.texts = LANGUAGES[self.current_lang]; self.setWindowTitle(self.texts["window_title"]); self.findChildren(QGroupBox)[0].setTitle(self.texts["dng_converter_path"]); self.dng_browse_btn.setText(self.texts["browse"]); self.findChildren(QGroupBox)[1].setTitle(self.texts["lang_select"]); self.raw_group.setTitle(self.texts["raw_to_dng_group"]); self.raw_group.findChildren(QLabel)[0].setText(self.texts["drop_raw_files"]); self.add_raw_btn.setText(self.texts["add"]); self.remove_raw_btn.setText(self.texts["remove"]); self.clear_raw_btn.setText(self.texts["clear"]); self.raw_group.findChildren(QLabel)[1].setText(self.texts["target_camera"]); self.raw_group.findChildren(QLabel)[2].setText(self.texts["output_folder"]); self.output_same_radio.setText(self.texts["same_as_source"]); self.output_custom_radio.setText(self.texts["select_folder"]); self.custom_folder_browse_btn.setText(self.texts["browse"]); self.convert_button.setText(self.texts["convert_button"]); self.jpg_group.setTitle(self.texts["jpg_restore_group"]); self.jpg_group.findChildren(QLabel)[0].setText(self.texts["drop_jpg_files"]); self.add_jpg_btn.setText(self.texts["add"]); self.remove_jpg_btn.setText(self.texts["remove"]); self.clear_jpg_btn.setText(self.texts["clear"]); self.remove_suffix_checkbox.setText(self.texts["remove_camera_name"]); self.restore_button.setText(self.texts["restore_button"])
        self.raw_table_widget.set_headers([self.texts["col_filename"], self.texts["col_model"], self.texts["col_status"]])
        self.jpg_table_widget.set_headers([self.texts["col_filename"], self.texts["col_model"], self.texts["col_status"]])
        self.statusBar().showMessage(self.texts["ready"])

    def browse_dng_converter(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Adobe DNG Converter", "", "Executable Files (*.exe)");
        if path: self.dng_path_edit.setText(path)
    def browse_output_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder");
        if path: self.custom_folder_path_label.setText(path); self.output_custom_radio.setChecked(True)
            
    def get_exif_info(self, file_path):
        normalized_file_path = os.path.normpath(file_path)
        command = f'& "{self.exiftool_path}" -Make -Model -UniqueCameraModel "{normalized_file_path}"'
        try:
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
            exif = {};
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':', 1);
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    if "Unique Camera Model" in key: exif["unique"] = value
                    elif "Model" in key: exif["model"] = value
                    elif "Make" in key: exif["make"] = value
            if "unique" not in exif and "make" in exif and "model" in exif: exif["unique"] = f"{exif['make']} {exif['model']}"
            return exif
        except subprocess.CalledProcessError as e: print(f"Error getting EXIF for {file_path}: {e.stderr}"); return None

    def add_files_to_table(self, table_widget, path_list, filepaths):
        new_files_added = False
        for path in filepaths:
            if path not in path_list:
                path_list.append(path)
                new_files_added = True
        if new_files_added:
            self.update_table_widget(table_widget, path_list)

    def update_table_widget(self, table_widget, path_list):
        table_widget.setRowCount(0)
        is_jpg_table = (table_widget == self.jpg_table_widget)
        completed_set = self.completed_jpg_paths if is_jpg_table else self.completed_raw_paths
        for path in path_list:
            exif = self.get_exif_info(path)
            if not exif: continue
            base_name, _ = os.path.splitext(os.path.basename(path))
            if not is_jpg_table: self.original_exif_data[base_name] = exif
            make, model = exif.get("make", ""), exif.get("model", "")
            display_model = f"{make} {model}"
            if make.upper() in ["CANON", "NIKON CORPORATION", "RICOH"]: display_model = model
            status_text = "✔️" if path in completed_set else "❌"
            if is_jpg_table and status_text == "❌":
                original_base_name = re.sub(r'_[A-Z0-9]+$', '', base_name)
                if original_base_name in self.original_exif_data:
                    original_exif = self.original_exif_data[original_base_name]
                    if original_exif.get("make") == make and original_exif.get("model") == model:
                        status_text = "✔️"
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            filename_item = QTableWidgetItem(os.path.basename(path))
            filename_item.setToolTip(path)
            filename_item.setData(Qt.UserRole, path)
            model_item = QTableWidgetItem(display_model)
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignCenter)
            table_widget.setItem(row_position, 0, filename_item)
            table_widget.setItem(row_position, 1, model_item)
            table_widget.setItem(row_position, 2, status_item)

    def add_raw_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select RAW files", "", "RAW Files (*.arw *.cr2 *.cr3 *.nef *.orf *.raf *.dng *.rw2 *.pef)");
        if files: self.add_files_to_table(self.raw_table_widget, self.raw_files_paths, files)
    def remove_raw_files(self):
        selected_rows = sorted(list(set(item.row() for item in self.raw_table_widget.selectedItems())), reverse=True)
        if not selected_rows: return
        for row in selected_rows:
            path_to_remove = self.raw_files_paths.pop(row)
            self.completed_raw_paths.discard(path_to_remove)
        self.update_table_widget(self.raw_table_widget, self.raw_files_paths)
    def clear_raw_files(self): 
        self.raw_files_paths.clear(); self.completed_raw_paths.clear(); self.raw_table_widget.setRowCount(0)
    def on_raw_files_dropped(self, filepaths): self.add_files_to_table(self.raw_table_widget, self.raw_files_paths, filepaths)
    def add_jpg_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select JPG files", "", "JPG Files (*.jpg *.jpeg)");
        if files: self.add_files_to_table(self.jpg_table_widget, self.jpg_files_paths, files)
    def remove_jpg_files(self):
        selected_rows = sorted(list(set(item.row() for item in self.jpg_table_widget.selectedItems())), reverse=True)
        if not selected_rows: return
        for row in selected_rows:
            path_to_remove = self.jpg_files_paths.pop(row)
            self.completed_jpg_paths.discard(path_to_remove)
        self.update_table_widget(self.jpg_table_widget, self.jpg_files_paths)
    def clear_jpg_files(self): 
        self.jpg_files_paths.clear(); self.completed_jpg_paths.clear(); self.jpg_table_widget.setRowCount(0)
    def on_jpg_files_dropped(self, filepaths): self.add_files_to_table(self.jpg_table_widget, self.jpg_files_paths, filepaths)

    def start_conversion(self):
        dng_path = self.dng_path_edit.text()
        if not dng_path:
            QMessageBox.warning(self, self.texts['error'], self.texts['dng_converter_not_found'])
            return
        if not self.raw_files_paths: return

        # 1. 선택된 카메라 목록 가져오기 및 유효성 검사
        selected_cameras = [cb.text() for cb in self.camera_checkboxes if cb.isChecked()]
        if not selected_cameras:
            # 번역키를 사용하여 메시지 표시
            QMessageBox.warning(self, self.texts['error'], self.texts['select_camera_msg'])
            return

        output_path = ""
        if self.output_same_radio.isChecked():
            if self.raw_files_paths: output_path = os.path.dirname(self.raw_files_paths[0])
        elif self.output_custom_radio.isChecked():
            output_path = self.custom_folder_path_label.text()

        if not output_path:
            QMessageBox.warning(self, self.texts['error'], self.texts['select_output_folder_msg'])
            return
        
        # 2. '폴더 지정' 시 해당 폴더가 실제로 존재하는지 확인
        if self.output_custom_radio.isChecked() and not os.path.isdir(output_path):
            QMessageBox.warning(self, self.texts['error'], self.texts['output_folder_not_exist_msg'])
            return
            
        options = {"dng_path": self.dng_path_edit.text(), "target_cameras": selected_cameras, "output_path": os.path.normpath(output_path)}
        
        self.worker = Worker('convert', self.raw_files_paths, options, self.exiftool_path)
        self.worker.progress.connect(self.update_status); self.worker.finished.connect(self.conversion_finished); self.worker.error.connect(self.show_error); self.worker.start(); self.convert_button.setEnabled(False); self.restore_button.setEnabled(False)



    def start_restore(self):
        if not self.jpg_files_paths: return
        options = {"original_exif_data": self.original_exif_data, "remove_suffix": self.remove_suffix_checkbox.isChecked()}
        self.worker = Worker('restore', self.jpg_files_paths, options, self.exiftool_path)
        self.worker.progress.connect(self.update_status); self.worker.finished.connect(self.restore_finished); self.worker.error.connect(self.show_error); self.worker.start(); self.convert_button.setEnabled(False); self.restore_button.setEnabled(False)

    def update_status(self, message): self.statusBar().showMessage(message)

    def update_status_column(self, table_widget, path_list, successful_paths):
        successful_set = set(successful_paths)
        for row, original_path in enumerate(path_list):
            if original_path in successful_set:
                status_item = QTableWidgetItem("✔️")
                status_item.setTextAlignment(Qt.AlignCenter)
                table_widget.setItem(row, 2, status_item)

    def conversion_finished(self, successful_paths):
        self.statusBar().showMessage(self.texts['ready']); QMessageBox.information(self, self.texts['conversion_complete'], f"{len(successful_paths)} {self.texts['files_processed_successfully']}")
        self.completed_raw_paths.update(successful_paths)
        self.update_status_column(self.raw_table_widget, self.raw_files_paths, successful_paths)
        self.convert_button.setEnabled(True); self.restore_button.setEnabled(True)

    def restore_finished(self, successful_paths):
        self.statusBar().showMessage(self.texts['ready']); QMessageBox.information(self, self.texts['exif_restore_complete'], f"{len(successful_paths)} {self.texts['files_processed_successfully']}")
        self.completed_jpg_paths.update(successful_paths)
        self.update_status_column(self.jpg_table_widget, self.jpg_files_paths, successful_paths)
        self.convert_button.setEnabled(True); self.restore_button.setEnabled(True)

    def show_error(self, message):
        self.statusBar().showMessage(self.texts['error']); QMessageBox.critical(self, self.texts['error'], message); self.convert_button.setEnabled(True); self.restore_button.setEnabled(True)
        
    def check_dng_converter_on_startup(self):
        if self.dng_path_edit.text(): return
        paths_to_check = [Path("C:/Program Files/Adobe/Adobe DNG Converter/Adobe DNG Converter.exe"), Path("D:/Program Files/Adobe/Adobe DNG Converter/Adobe DNG Converter.exe")]
        found_path = next((str(p) for p in paths_to_check if p.exists()), None)
        if found_path:
            self.dng_path_edit.setText(found_path)
            if not self.settings.value("first_launch_success_shown", False, type=bool): QMessageBox.information(self, "Info", self.texts["dng_converter_found"]); self.settings.setValue("first_launch_success_shown", True)
        elif not self.settings.value("first_launch_fail_shown", False, type=bool): QMessageBox.warning(self, "Warning", self.texts["dng_converter_not_found"]); self.settings.setValue("first_launch_fail_shown", True)

    def save_settings(self):
        self.settings.setValue("dng_converter_path", self.dng_path_edit.text()); self.settings.setValue("language", self.current_lang); self.settings.setValue("custom_output_folder", self.custom_folder_path_label.text()); self.settings.setValue("output_folder_is_custom", self.output_custom_radio.isChecked()); self.settings.setValue("remove_suffix_checked", self.remove_suffix_checkbox.isChecked())
    def load_settings(self):
        self.dng_path_edit.setText(self.settings.value("dng_converter_path", "")); lang = self.settings.value("language", "en"); (self.radio_ko if lang == "ko" else self.radio_en).setChecked(True); self.custom_folder_path_label.setText(self.settings.value("custom_output_folder", ""))
        if self.settings.value("output_folder_is_custom", False, type=bool): self.output_custom_radio.setChecked(True)
        else: self.output_same_radio.setChecked(True)
        self.remove_suffix_checkbox.setChecked(self.settings.value("remove_suffix_checked", False, type=bool))
        
    def load_original_exif_data(self):
        if os.path.exists(self.exif_data_file):
            with open(self.exif_data_file, 'r', encoding='utf-8') as f:
                try: self.original_exif_data = json.load(f)
                except json.JSONDecodeError: pass

    def save_original_exif_data(self):
        with open(self.exif_data_file, 'w', encoding='utf-8') as f: json.dump(self.original_exif_data, f, indent=4, ensure_ascii=False)
    def closeEvent(self, event):
        self.save_settings(); self.save_original_exif_data(); event.accept()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    dark_stylesheet = """
        QWidget { background-color: #2b2b2b; color: #f0f0f0; font-size: 10pt; }
        QMainWindow { background-color: #2b2b2b; }
        QGroupBox { font-weight: bold; border: 1px solid #444; border-radius: 5px; margin-top: 1ex; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
        QLineEdit, QComboBox, QTableWidget { background-color: #3c3c3c; border: 1px solid #555; border-radius: 3px; padding: 5px; }
        QTableWidget { gridline-color: #444; }
        QTableWidget::item:alternate { background: #363636; }
        QTableWidget::item:selected { background: #6E6E6E; color: #FFFFFF; }
        QHeaderView::section { background-color: #444; color: #ccc; padding: 4px; border: 1px solid #555; font-weight: bold; }
        QPushButton { background-color: #6E6E6E; color: #FFFFFF; border: none; padding: 8px 16px; border-radius: 4px; } QPushButton:hover { background-color: #8C8C8C; } QPushButton:pressed { background-color: #555555; } QPushButton:disabled { background-color: #555; color: #888; }
        QRadioButton::indicator, QCheckBox::indicator { width: 14px; height: 14px; }
    """
    app.setStyleSheet(dark_stylesheet)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())