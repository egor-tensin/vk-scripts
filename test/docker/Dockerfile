ARG DISTRO=noble

FROM ubuntu:$DISTRO

RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
        ca-certificates \
        make \
        python3 \
        python3-matplotlib

COPY [".", "/src"]
WORKDIR /src
CMD ["make", "test"]
