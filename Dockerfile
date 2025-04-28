# Build with:
# docker build --network host . -t lucaschess
# Run With:
# docker run -it -e "DISPLAY=$DISPLAY" -v "$HOME/.Xauthority:/lucaschess/.Xauthority:ro" -v "$PWD/UserData:/lucaschess/UserData" --network host --rm lucaschess

FROM python:3.13-bullseye
WORKDIR /lucaschess/
ENV HOME=/lucaschess/

RUN apt-get update && \
    apt-get install -y --no-install-recommends portaudio19-dev libqt5gui5 libpulse-mainloop-glib0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

WORKDIR /lucaschess/bin/_fastercode
RUN chmod a+x ./linux64.sh && ./linux64.sh

WORKDIR /lucaschess/bin/OS/linux
RUN chmod a+x ./RunEngines && ./RunEngines

WORKDIR /lucaschess/bin
RUN chmod a+x LucasR.py

# Create and switch to a non-root user
RUN useradd -ms /bin/bash lucaschess && chown -R lucaschess:lucaschess /lucaschess
USER lucaschess

# To debug problems with Qt, enable the following line:
# ENV QT_DEBUG_PLUGINS=1

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["./LucasR.py", "-healthcheck"]

CMD ["./LucasR.py"]
