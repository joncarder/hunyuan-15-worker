FROM runpod/worker-comfyui:5.7.1-base

# Add --highvram flag to ComfyUI startup
RUN find / -name "*.sh" -exec grep -l "main.py" {} \; 2>/dev/null | head -5 || true
RUN sed -i 's/python.*main\.py/python main.py --highvram/g' /comfyui/main.py 2>/dev/null || \
    sed -i 's/python main\.py/python main.py --highvram/g' /start.sh 2>/dev/null || \
    echo "Manual flag injection needed"

ENV COMFYUI_FLAGS="--highvram"
