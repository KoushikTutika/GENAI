# ChromaDB Installation Fix

## Problem
Python 3.14 is too new. ChromaDB dependencies (onnxruntime, chroma-hnswlib) don't have pre-built wheels for Python 3.14 yet.

## Solution
Install Python 3.11 or 3.12 from https://www.python.org/downloads/

Then run:
```
python -m pip install chromadb
```

## Alternative (if you must use Python 3.14)
Wait for chromadb dependencies to release Python 3.14 compatible wheels, or install Visual Studio Build Tools to compile from source.
