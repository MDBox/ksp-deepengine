FROM nvidia/cudagl:9.1-runtime

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y python3 python3-pip python-opengl libopenblas-dev && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --set libblas.so.3 /usr/lib/openblas-base/libblas.so.3

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        wget \
	    curl \
	    nano \
	    vim \
        libatlas-base-dev \
        libboost-all-dev \
        libgflags-dev \
        libgoogle-glog-dev \
        libhdf5-serial-dev \
        libleveldb-dev \
        liblmdb-dev \
        libopencv-dev \
        libprotobuf-dev \
        libsnappy-dev \
        protobuf-compiler \
        python-dev \
        python-numpy \
        python-pip \
        python-setuptools \
        python-scipy && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip3 install --upgrade pip

RUN pip3 install --ignore-installed tabulate requests opencv-python jupyter jupyterlab tensorflow-gpu gym sklearn matplotlib gensim scipy numpy --no-cache-dir
RUN jupyter serverextension enable --py jupyterlab --sys-prefix

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF \
	&& apt update \
	&& apt install -y apt-transport-https \
	&& echo "deb https://download.mono-project.com/repo/ubuntu stable-xenial main" | tee /etc/apt/sources.list.d/mono-official-stable.list \
	&& apt update \
	&& apt install -y mono-complete mono-devel mono-dbg ca-certificates-mono mono-xsp4 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR "/root"
COPY ./config/jupyter ./.jupyter
RUN mkdir project

CMD jupyter-lab

ENV DISPLAY=:0

LABEL com.nvidia.volumes.needed="nvidia_driver"

EXPOSE 8888 6006 5000
