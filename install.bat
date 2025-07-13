@echo off

echo Installing dependencies
pip install -r requirements.txt
echo Dependencies installed successfully


echo Checking if Required Models are Downloaded
set "SRC_DIR=%~dp0src"
rem File names to look for
set "CLIP_MODEL=openai_clip.onnx"
set "FACE_MODEL=mediapipe_face-facelandmarkdetector-float.onnx"

rem ----- Check the OpenAI CLIP model ------------------------------
if not exist "%SRC_DIR%\%CLIP_MODEL%" (
    echo Get OpenAI-Clip Model if Not already present
    echo Please Download from Qualcomm AI Hub
)

rem ----- Check the Face-detection / Face-mesh model ---------------
if not exist "%SRC_DIR%\%FACE_MODEL%" (
    echo Get Facial Detection Model if Not already present
    echo Please Download from Qualcomm AI Hub
)