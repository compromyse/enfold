{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs, ... }: let
      pkgs = import nixpkgs { system = "x86_64-linux"; config.allowUnfree = true; };
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          (python3.withPackages (p: [
            p.selenium
            p.opencv-python
            p.pytesseract
            p.beautifulsoup4
            p.tinydb
            p.fastapi
            p.uvicorn
            p.jinja2
          ]))
          pyright

          firefox
          geckodriver

          tesseract
        ];
      };
    };
}
