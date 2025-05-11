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
          p.easyocr
          p.beautifulsoup4
          p.tinydb
          p.fastapi
          p.uvicorn
          p.jinja2
          p.streamlit
          p.gradio
          p.pycryptodome

          p.flask
          p.flask-login
          p.rq

          p.mitmproxy

          p.pdf2image
          p.argostranslate
          # p.openai-whisper
          # p.torch-bin
        ]))

        apktool
        openjdk8

        python3Packages.pymupdf
        mupdf

        pyright

        firefox
        geckodriver

        tesseract

        nodejs_22
        vtsls

        redis
      ];
    };
  };
}
