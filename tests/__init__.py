import sys, os
os.environ["FLASK_ENV"] = "Test"
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
