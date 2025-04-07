{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs, ... }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; config.allowUnfree = true; };
  in {
    devShells.${system}.default = pkgs.mkShell {
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
          p.streamlit
          p.gradio

          # p.pdf2image
          # p.openai-whisper
          # p.torch-bin
        ]))

        pyright

        firefox
        geckodriver

        tesseract

        nodejs_22
        vtsls
      ];
    };
  };
}
