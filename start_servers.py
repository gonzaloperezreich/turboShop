import subprocess

def start_flask():
    # Iniciar la aplicación Flask
    subprocess.Popen(["python", "app.py"])

def start_node():
    # Iniciar el servidor Node.js
    subprocess.Popen(["npm", "run", "dev"], cwd="server")

if __name__ == "__main__":
    start_flask()
    start_node()
