FROM pedros007/debian-gdal:2.2.2

LABEL authors="Jon Duckworth <jon.duckworth@digitalglobe.com>, Jon Saints <jon.saints@digitalglobe.com>"

RUN apt-get update && apt-get install git-core

COPY .gitconfig /root/.gitconfig

# Install tippecanoe
ARG TIPPECANOE_RELEASE="1.26.3"

WORKDIR /tmp
RUN git clone https://github.com/mapbox/tippecanoe.git tippecanoe && \
    cd tippecanoe && \
    git checkout tags/$TIPPECANOE_RELEASE && \
    make && \
    make install && \
    cd /tmp && \
    rm -rf tippecanoe

# Return versions by default
CMD echo `gdalinfo --version` && echo `tippecanoe -v`