# General settings.
debug = False
task = ""

# PDFium settings.
# chromium/8066 matches bblanchon.PDFium 156.0.8066, which is the P/Invoke
# layout miniocr already calls (FPDF_LIBRARY_CONFIG version 4).
pdfium_git_branch = "chromium/8066"
# The branch reference is https://pdfium.googlesource.com/pdfium/+/refs/heads/chromium/8066.
# Changing it also requires changing docker/android/Dockerfile and docker/wasm/Dockerfile.

# Emscripten SDK settings.
emsdk_version = "6.0.0"
# Changing it also requires changing docker/wasm/Dockerfile.

# Settings for macOS.
configurations_macos = ["release"]
shared_lib_macos = False
targets_macos = [
    {"target_os": "macos", "target_cpu": "x64", "pdfium_os": "mac"},
    {"target_os": "macos", "target_cpu": "arm64", "pdfium_os": "mac"},
]

# Settings for Linux.
configurations_linux = ["release"]
shared_lib_linux = True
# CI builds x64 only. arm64 is still a valid target_cpu if you add it back.
targets_linux = [
    {"target_os": "linux", "target_cpu": "x64", "pdfium_os": "linux"},
]
# "minimal" skips third_party/skia. "small" still checks Skia out and skips
# the full waterfall. Both renderers stay in the binary so m_RendererType
# can select AGG or Skia at FPDF_InitLibraryWithConfig.
pdfium_checkout_configuration_linux = "small"
pdf_use_skia_linux = True
pdf_use_agg_linux = True

# Settings for Windows.
configurations_windows = ["release"]
shared_lib_windows = True
targets_windows = [
    {"target_os": "windows", "target_cpu": "x64", "pdfium_os": "win"},
    {"target_os": "windows", "target_cpu": "arm64", "pdfium_os": "win"},
]

# Settings for iOS.
configurations_ios = ["release"]
shared_lib_ios = False
targets_ios = [
    {
        "target_os": "ios",
        "target_cpu": "arm64",
        "pdfium_os": "ios",
        "target_environment": "device",
    },
    {
        "target_os": "ios",
        "target_cpu": "x64",
        "pdfium_os": "ios",
        "target_environment": "simulator",
    },
    {
        "target_os": "ios",
        "target_cpu": "arm64",
        "pdfium_os": "ios",
        "target_environment": "simulator",
    },
]

# Settings for Android.
configurations_android = ["release"]
shared_lib_android = True
targets_android = [
    {
        "target_os": "android",
        "target_cpu": "arm",
        "pdfium_os": "android",
        "android_cpu": "armeabi-v7a",
    },
    {
        "target_os": "android",
        "target_cpu": "x86",
        "pdfium_os": "android",
        "android_cpu": "x86",
    },
    {
        "target_os": "android",
        "target_cpu": "arm64",
        "pdfium_os": "android",
        "android_cpu": "arm64-v8a",
    },
    {
        "target_os": "android",
        "target_cpu": "x64",
        "pdfium_os": "android",
        "android_cpu": "x86_64",
    },
]

# Settings for WASM.
configurations_wasm = ["release"]
shared_lib_wasm = False
targets_wasm = [
    {"target_os": "emscripten", "target_cpu": "wasm", "pdfium_os": "emscripten"},
]
