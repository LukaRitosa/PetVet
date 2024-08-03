from python:3.12
workdir app/
copy requirements.txt req.txt
run pip install -r req.txt
copy . .
expose 8080
cmd ["python","main.py"]
