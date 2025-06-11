{
  description = "Set up Python environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: 
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells.default = pkgs.mkShell {
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
        };
      });
}

