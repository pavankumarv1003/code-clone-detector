# --- STAGE 1: Define the Base Environment ---

# FROM python:3.9-slim
# This is the starting point. It tells Docker to use an official, pre-built image 
# that already has Python 3.9 installed. The "-slim" version is a smaller, 
# lightweight version, which is good for faster downloads and smaller final images.
FROM python:3.9-slim


# --- STAGE 2: Set up the Workspace and Install Dependencies ---

# WORKDIR /app
# This sets the "working directory" inside the container. All subsequent commands 
# (like COPY and RUN) will be executed from this /app folder. It's like running `cd /app`.
WORKDIR /app

# COPY requirements.txt .
# This copies ONLY the requirements.txt file from your local project folder into 
# the container's /app directory. We do this first because Docker caches layers. 
# If requirements.txt doesn't change, Docker can reuse the installed libraries layer,
# making future builds much faster. The "." means "copy it to the current directory (/app)".
COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt
# This executes a command inside the container. It runs pip to install all the 
# libraries listed in your requirements.txt file. `--no-cache-dir` is a good practice 
# to keep the final image size smaller by not storing the download cache.
RUN pip install --no-cache-dir -r requirements.txt


# --- STAGE 3: Copy Your Application Code ---

# COPY . .
# This command copies EVERYTHING ELSE from your local project folder into the 
# container's /app directory. This includes your app.py, your .h5 and .pkl files, 
# and the templates/ folder. The first "." means "everything in the current local directory"
# and the second "." means "paste it into the current container directory (/app)".
COPY . .


# --- STAGE 4: Configure and Run the Application ---

# EXPOSE 7860
# This is like a piece of documentation. It informs Docker that the container will 
# listen on port 7860 at runtime. Hugging Face Spaces and other platforms use this 
# to know which port to route traffic to. It doesn't actually open the port; 
# the Gunicorn command does that.
EXPOSE 7860

# CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "app:app"]
# This is the final command that will be executed when the container starts.
# It does NOT run during the build process.
# - "gunicorn": The production web server we installed.
# - "--bind", "0.0.0.0:7860": Tells Gunicorn to listen for incoming connections from any IP address ("0.0.0.0") on port 7860.
# - "--workers", "1": Specifies how many worker processes to run. For a small app on a free tier, 1 is sufficient.
# - "app:app": This is the most important part. It tells Gunicorn: "Look inside the file named 'app.py' and run the Flask application object named 'app'".
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "app:app"]