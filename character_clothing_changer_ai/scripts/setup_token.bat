@echo off
echo Setting up HuggingFace Token...
cd /d %~dp0..
python setup_hf_token.py
pause

