The code content is from RealPython (https://www.youtube.com/watch?v=lXeUBr6S5bk&list=WL&index=617)

Development:
1. Create all the file structure with empty .py files
2. Create the library/pyproject.toml and add the setuptools info
3. Run the following command for installation:

(code_study) deepspace9@Rays-Mac-mini tic-tac-toe % pip install --editable library/
Obtaining file:///Users/deepspace9/DevCore/code_study/GAME/tic-tac-toe/library
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Preparing editable metadata (pyproject.toml) ... done
Building wheels for collected packages: tic-tac-toe
  Building editable for tic-tac-toe (pyproject.toml) ... done
  Created wheel for tic-tac-toe: filename=tic_tac_toe-1.0.0-0.editable-py3-none-any.whl size=1232 sha256=0e80fdff855427751ffba9d18c93c8027cd338127709d3ce39f69a04dcd82fa1
  Stored in directory: /private/var/folders/7r/wmv6h47s43nchl2pwgq8gcgh0000gn/T/pip-ephem-wheel-cache-urx2uyqg/wheels/ad/28/77/cf5299257668224f34abdb6907c156eeb05b0253a84bae11ec
Successfully built tic-tac-toe
Installing collected packages: tic-tac-toe
  Attempting uninstall: tic-tac-toe
    Found existing installation: tic-tac-toe 0.1.0
    Uninstalling tic-tac-toe-0.1.0:
      Successfully uninstalled tic-tac-toe-0.1.0
Successfully installed tic-tac-toe-1.0.0
(code_study) deepspace9@Rays-Mac-mini tic-tac-toe %

