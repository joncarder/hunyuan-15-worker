FROM runpod/worker-comfyui:5.7.1-base

# Sanity check so the GitHub Actions log shows what Python and pip we are using
RUN python -V && pip -V

# Upgrade pip tooling (helps with dependency resolution)
RUN python -m pip install --upgrade pip setuptools wheel

# SageAttention dependency and a safe pinned SageAttention version
RUN python -m pip install "triton>=3.0.0" "sageattention==1.0.6"

# Add --highvram flag to ComfyUI startup
RUN find / -name "*.sh" -exec grep -l "main.py" {} \; 2>/dev/null | head -5 || true
RUN sed -i 's/python.*main\.py/python main.py --highvram/g' /comfyui/main.py 2>/dev/null || \
    sed -i 's/python main\.py/python main.py --highvram/g' /start.sh 2>/dev/null || \
    echo "Manual flag injection needed"

ENV COMFYUI_FLAGS="--highvram"
