with open('train_window_v4.py', 'r') as f:
    c = f.read()
c = c.replace(\"cv='prefit'\", \"cv=3\")
with open('train_window_v4.py', 'w') as f:
    f.write(c)
