# Use an official Python runtime as a parent image
FROM continuumio/miniconda3

RUN apt-get --allow-releaseinfo-change update
RUN apt-get install -y build-essential 

RUN mkdir /tmp/hit_map
COPY ./ /tmp/hit_map/
RUN pip install /tmp/hit_map

RUN rm -rf /tmp/hit_map

ENTRYPOINT ["/opt/conda/bin/hit_mapcmd.py"]

CMD ["--help"]
