CreateVectorTiles Task
=====

A GBDX task to create vector tiles from any valid OGR datasource.

## Building Docker Image

1. Create a `.gitconfig` file in the main directory with valid username and password credentials

    This is required in order to clone `tippecanoe` as part of the build process.

2. `docker build -t create-vector-tiles:<version> -t create-vector-tiles:latest .`

## Testing

1. Place your test data in `test-mnt/input/data`. Input datasets can be in any valid OGR format (have not tested this thoroughly). Multi-file formats should be in a single directory within `test-mnt/input/data`.

2. Create `ports.json` file in `test-mnt/input` (see `test-mnt/input/ports.template.json` as an example).

3. `docker-compose up test`

