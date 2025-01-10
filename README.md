# Art Prices Search Engine

This project involved designing and implementing a Python-based search engine to help users estimate market prices for digital artwork. The project aimed at collecting data on digital art, processing it to facilitate efficient searching, and developing the search functionality itself.

## Project Overview

This project is organized in a Python script used for the web scraping and two Jupyter notebooks. The former scrapes two websites, resulting in two datasets containing data on a total of approximately 6000 artworks, with information on price, author, title, size, tags and descriptions. The processing notebook handles data preparation tasks, including tokenization, the removal of stopwords and topic modeling using Top2Vec. The final notebook implements the search functionality, enabling users to query and explore the data effectively.

## Requirements

The following Python libraries are needed:

  - `bs4`
  - `pandas`
  - `nltk`
  - `pROC`
  - `matplotlib`
  - `top2vec`
  - `selenium`
  