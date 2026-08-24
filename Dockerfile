FROM python:3.10

# Links the GHCR package to this repository. Without image.source the package
# is orphaned: it shows no repo, no README, and a reduced settings page.
LABEL org.opencontainers.image.source="https://github.com/sgtsquiggs/speedrr"
LABEL org.opencontainers.image.description="speedrr, patched to run on qBittorrent 5.2+"
LABEL org.opencontainers.image.licenses="GPL-3.0"

ADD . /home

WORKDIR /home

RUN pip install -r requirements.txt

CMD ["python", "./main.py"]
