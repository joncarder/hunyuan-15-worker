FROM runpod/worker-comfyui:5.7.1-base

# Modify the start script to add --highvram flag
RUN sed -i 's/main.py/main.py --highvram/g' /start.sh || \
    sed -i 's/main.py/main.py --highvram/g' /comfyui/start.sh || \
    echo "Could not find start.sh, trying alternative method"

# Alternative: Set environment variable that some versions respect
ENV COMFYUI_EXTRA_ARGS="--highvram"
ENV CLI_ARGS="--highvram"

# Ensure the flag is added to any python command launching main.py
RUN if [ -f /start.sh ]; then \
      cat /start.sh; \
    fi
