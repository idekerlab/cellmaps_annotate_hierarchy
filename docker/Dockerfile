# Use an official Python runtime as a parent image
FROM continuumio/miniconda3

RUN apt-get --allow-releaseinfo-change update
RUN apt-get install -y build-essential 

RUN mkdir /tmp/cellmaps_annotate_hierarchy
COPY ./ /tmp/cellmaps_annotate_hierarchy/
RUN pip install /tmp/cellmaps_annotate_hierarchy

RUN rm -rf /tmp/cellmaps_annotate_hierarchy

ENTRYPOINT ["/opt/conda/bin/cellmaps_annotate_hierarchycmd.py"]

CMD ["--help"]
