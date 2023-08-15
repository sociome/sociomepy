# sociomepy
sociomepy is an open-source Python toolkit that can access the datasets in the Sociome Data Commons (SDC).
The SDC is a cloud-based data repository with a variety of datasets describing social, environmental, behavioral, and psychological exposures/circumstances connected with locations. Each dataset is stored in a geocoded format, called GeoJSON, where measurements are associated with latitude and longitude regions. This format is supported by all major GIS frameworks. The SDC makes it easy to run integrative queries across the datasets, i.e., to identify all of the exposures associated with a particular geographical unit ranging from an individual location to an entire zip code.

These exposure profiles can be pulled into a protected enclave where these geocoded non-clinical data can be joined to clinical data (be that limited data sets or full PHI data). Each dataset is documented with metadata describing its scope, quality, and units of measure. The repository is searchable and datasets can be directly accessed by researchers through a programmatic interface. Researchers can identify the types of exposures they wish to investigate and easily build an integrated profile for a certain region. sociomepy is the API layer that allows datasets to be pulled into a clinical data enclave.

# Getting Started
The following instructions assume basic familiarity with Python programming and packaging. We will eventually release more accessible instructions.

First, clone the `sociomepy` repository:
```
git clone https://github.com/sociome/sociomepy.git
```

To install `sociomepy` locally, run the following:
```
cd sociomepy
pip install .
```

To test whether `sociomepy` is properly installed, run:
```
python
>>> import sociomepy
```
That code should execute without any errors.

# Documentation
We will illustrate the functionality with a few example code notebooks. First, download some example data [https://drive.google.com/drive/folders/1XvWepRqLApQZ6xpkeG6k-30DnEzj_1Br?usp=sharing] store this data in a folder "data" outside of sociomepy. The directory structure should look like this:
```
..
\_ data
\_ sociomepy
```
Run the following code,
```
cd sociomepy
jupyter notebook
```
From the Jupyter notebook interface click on the "docs" folder, and go through any of the walk throughs.

