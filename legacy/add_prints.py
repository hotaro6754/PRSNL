with open('train_window_v3.py', 'r') as f:
    content = f.read()

content = "import sys\nprint('Starting script...')\nsys.stdout.flush()\n" + content

with open('train_window_v3.py', 'w') as f:
    f.write(content)
