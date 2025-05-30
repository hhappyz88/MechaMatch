# Base image with Conda
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app/scraper

# Copy ONLY the env first to leverage Docker cache
COPY ./environment.yml .

# Build Conda environment (name must match .yml)
RUN conda env create -f environment.yml

# Activate conda env for all future RUN/CMD
SHELL ["/bin/bash", "-c"]

# Now copy the rest of your project (Scrapy code)
COPY ./ /app/scraper/

# Set the default command (can be overridden)
ENTRYPOINT ["conda", "run", "-n", "mecha_match", "python", "run_spiders.py"]
CMD [""]