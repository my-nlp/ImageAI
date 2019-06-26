FROM python:3.7

RUN apt-get update \
    && apt-get install -y \
        build-essential \
        supervisor \
        cmake \
        curl \
        git \
        wget \
        unzip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install numpy tensorflow scipy opencv-python pillow matplotlib h5py keras
RUN pip3 install https://github.com/OlafenwaMoses/ImageAI/releases/download/2.0.2/imageai-2.0.2-py3-none-any.whl 

COPY /app/* /app/

COPY supervisord-videoai.conf /etc/supervisor/conf.d/supervisord-videoai.conf

WORKDIR /

EXPOSE 5000 9191

ENTRYPOINT [ "supervisord", "-n" ]