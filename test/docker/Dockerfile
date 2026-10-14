ARG DISTRO=noble

FROM ubuntu:$DISTRO

RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
        make \
        python3

COPY [".", "/src"]
WORKDIR /src
CMD ["make", "test"]
