# Dockerfile
#
# Phase F goal: prove the app runs identically inside a container, not
# just on your laptop. This catches "works on my machine" problems before
# they become "works nowhere but my machine" problems.
# Start from an official, minimal Python image rather than a full OS image.
# "slim" keeps the image smaller without missing anything Python needs.
FROM python:3.12-slim
# All subsequent commands run from this directory inside the container.
WORKDIR /app
# Don't buffer print() statements.
ENV PYTHONUNBUFFERED=1
# Copy just requirements.txt first (not the whole project yet).
# This is a deliberate ordering trick: Docker caches each step, so if only
# your code changes (not your dependencies), Docker can reuse the cached
# "pip install" step instead of re-running it every time. Faster rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Now copy the rest of the project files in.
COPY main.py .
COPY app.py .
COPY test_main.py .
# Document which port the container listens on. Render also reads this
# from its own dashboard/PORT env var at runtime - this line is mainly
# for humans reading the Dockerfile, not strictly required by Render.
EXPOSE 8080
# What runs when someone does `docker run` on this image, with no other
# command specified. Uses gunicorn (a production WSGI server) instead of
# Flask's built-in dev server, and reads $PORT from the environment since
# Render assigns that dynamically rather than always using 8080.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:$PORT app:app"]