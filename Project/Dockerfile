# 1. Use a lightweight Python image
FROM python:3.10-slim
# 2. Set the working directory
WORKDIR /app
# 3. Copy the requirements file and install dependencies
COPY  requirements.txt .
RUN pip install -r requirements.txt
# 4. Copy the rest of your code
COPY . .
# 5. Expose the port (Flask usually uses 5000, Django uses 8000)
EXPOSE 5000
# 6. Run the application 
# NOTE: Change "app.py" to your actual main python file name if it's different
CMD ["python", "app.run"]
