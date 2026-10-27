FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/home/user
RUN useradd --uid 1000 --create-home --shell /bin/bash user
WORKDIR /home/user/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY --chown=user:user app.py deployment.json ./
COPY --chown=user:user frontierlab/ ./frontierlab/
COPY --chown=user:user datasets/ ./datasets/
COPY --chown=user:user docs/ ./docs/
USER user
EXPOSE 7860
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=7860", "--server.headless=true", "--browser.gatherUsageStats=false"]
