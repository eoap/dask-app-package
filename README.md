# Dask application package

This repository contains two application package examples to demonstrate how `calrissian` CWL runner manages Dask resources via a dedicated extension.

The application packages are: 

* A Sentinel-2 Monthly Mosaic Generator

    This application package monthly median mosaics from Sentinel-2 imagery using STAC data sources. It retrieves Sentinel-2 data from the Planetary Computer STAC API, processes the data with Dask and Xarray, and stores the results as Cloud-Optimized GeoTIFFs (COGs) with an associated SpatioTemporal Asset Catalog (STAC).

    Features:
    - Retrieves Sentinel-2 imagery based on a time range and area of interest (AOI).
    - Filters images by cloud cover.
    - Generates monthly median mosaics.
    - Saves mosaics as Cloud-Optimized GeoTIFFs (COGs).
    - Creates a STAC catalog for easy data access and discovery.
    - Uses Dask for parallel processing.


* EOPF Sentinel-2 RGB composite and vegetation index

    This application package reads an EOPF Sentinel-2 product and produces RGB composites and vegetation indexes

