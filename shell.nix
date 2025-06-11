{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python312
    pkgs.python312Packages.virtualenv
  ];

  shellHook = ''
    VENV=".venv"
    if [ ! -d "$VENV" ]; then
      virtualenv "$VENV"
      source "$VENV/bin/activate"
      if [ -f requirements.txt ]; then
        pip install -r requirements.txt
      fi
    else
      source "$VENV/bin/activate"
    fi
  '';
}

