# Use the official Selenium Chrome standalone image which has Chrome and ChromeDriver installed
FROM selenium/standalone-chrome:latest

# Set working directory inside container
WORKDIR /app

# Copy your app files into the container
COPY . /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Expose port 10000 (or whatever your Flask app runs on)
EXPOSE 10000

# Run the Flask app using python3
CMD ["python3", "app.py"]
