# Hugging Face Spaces CPU Basic: only the Streamlit UI, research retrieval & audits.
# No paid model API; never attempts to load the 17GB Muse Glimmer checkpoint.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/user

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --uid 1000 --create-home --shell /bin/bash user
WORKDIR /home/user/app

# Public user-controlled competition repository; rebuilt Space picks up the latest main.
# To use a frozen version, pin this git checkout to a reviewed commit instead.
RUN git clone --depth 1 https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026.git . \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && chown -R user:user /home/user/app

USER user
EXPOSE 7860
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=7860", "--server.headless=true", "--browser.gatherUsageStats=false"]
