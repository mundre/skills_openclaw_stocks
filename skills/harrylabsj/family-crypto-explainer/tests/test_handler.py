import sys
sys.path.insert(0, '..')
from handler import handle
result = handle({})
assert result["result"] == "done"
print("passed")
