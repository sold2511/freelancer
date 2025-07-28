FROM python

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install system dependencies and add missing apt configs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        netcat-openbsd \
        curl \
        gnupg \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY req.txt /code/
RUN pip install --upgrade pip
RUN pip install -r req.txt

# Copy project
COPY . /code/

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
