# Handwriting-to-Text OCR + LLM Refinement

**Hybrid AI Pipeline for Improving OCR Quality in Handwritten
Documents**

------------------------------------------------------------------------

# Project Overview

This project implements a **hybrid document-processing pipeline** that
converts handwritten PDFs into readable digital text.

The system combines:

-   **Azure Computer Vision OCR** -- extracts text from handwritten
    documents\
-   **Large Language Models (Mistral via Ollama)** -- refines OCR output
    by correcting spelling errors and broken words

The goal is to improve the **readability and usability of OCR results**
while preserving the original content of handwritten notes.

------------------------------------------------------------------------

# Quick Navigation

1.  Installation\
2.  Running the Project\
3.  OCR Processing Pipeline\
4.  LLM Refinement System\
5.  Output Files\
6.  Understanding the Results\
7.  Example Workflow\
8.  Limitations\
9.  Troubleshooting

------------------------------------------------------------------------

# Installation

## Prerequisites

Python 3.8+\
4GB RAM recommended\
Internet connection for Azure OCR

------------------------------------------------------------------------

## Install Dependencies

pip install requests python-dotenv

------------------------------------------------------------------------

## Install Ollama (Local LLM)

Download Ollama:

https://ollama.ai

Install the Mistral model:

ollama pull mistral

Ensure the Ollama server is running before executing the pipeline.

------------------------------------------------------------------------

# Azure Setup

## Create Azure Computer Vision Resource

1.  Open Azure Portal\
2.  Create a Computer Vision resource\
3.  Copy the following credentials:

AZURE_ENDPOINT\
AZURE_KEY

------------------------------------------------------------------------

## Configure Environment Variables

Create a `.env` file in the project directory:

AZURE_ENDPOINT=your_endpoint_here\
AZURE_KEY=your_key_here

------------------------------------------------------------------------

# File Structure

project/

main.py \# OCR + LLM pipeline\
input.pdf \# Handwritten document\
raw_ocr_output.json \# Full OCR response\
raw_text.txt \# Raw OCR text\
cleaned_text.txt \# LLM refined output\
low_confidence_report.json \# OCR confidence analysis\
README.md

------------------------------------------------------------------------

# Running the Project

## Complete Pipeline

Place a handwritten document in the project folder:

input.pdf

Run the script:

python main.py

------------------------------------------------------------------------

## What the Pipeline Does

Handwritten PDF\
↓\
Azure OCR Recognition\
↓\
Extract Raw Text\
↓\
Confidence Analysis\
↓\
LLM Text Refinement\
↓\
Clean Digital Output

Typical runtime: **1--3 minutes depending on document size**

------------------------------------------------------------------------

# OCR Processing Pipeline

## Step 1 --- OCR Extraction

The system sends the PDF to **Azure Computer Vision Read API** for
handwriting recognition.

Azure returns structured data including:

-   recognized text lines\
-   word confidence scores\
-   page layout information

------------------------------------------------------------------------

## Step 2 --- Raw Text Extraction

The recognized text is extracted and stored in:

raw_text.txt

This represents the **unprocessed OCR output**.

Example:

private sector on market is playing dominant role\
NGOS, pressure groups are intrusts groups

------------------------------------------------------------------------

# LLM Refinement System

## Purpose

OCR errors often appear as:

inclitutions\
intrusts groups\
administration erelationship

The LLM post‑processing stage attempts to correct these errors.

------------------------------------------------------------------------

## Example Correction

Raw OCR:

NGOS, pressure groups are intrusts groups

LLM Corrected:

NGOs, pressure groups are interest groups

------------------------------------------------------------------------

# Output Files

The pipeline generates several outputs.

## raw_ocr_output.json

Full OCR response returned by Azure including bounding boxes and
confidence scores.

## raw_text.txt

Direct OCR text extraction.

## cleaned_text.txt

LLM refined output with corrected spelling and formatting.

## low_confidence_report.json

List of lines where OCR confidence is low.

------------------------------------------------------------------------

# Understanding the Results

OCR performance depends heavily on:

-   handwriting clarity
-   scan quality
-   lighting conditions
-   document resolution

The LLM improves readability by correcting:

-   spelling mistakes
-   broken words
-   grammar inconsistencies
-   formatting issues

However, it **cannot recover completely illegible handwriting**.

------------------------------------------------------------------------

# Limitations

-   OCR errors with completely incorrect characters may not be
    recoverable\
-   Very poor handwriting may produce unusable OCR output\
-   LLM correction may occasionally modify sentence structure

------------------------------------------------------------------------

# Troubleshooting

## Azure API Error

Verify that the following values are correctly set in `.env`:

AZURE_ENDPOINT\
AZURE_KEY

------------------------------------------------------------------------

## LLM Not Responding

Ensure Ollama is running:

ollama run mistral

------------------------------------------------------------------------

## Missing Python Modules

Install dependencies:

pip install requests python-dotenv

------------------------------------------------------------------------

# Future Improvements

Possible extensions include:

-   Web interface for document uploads\
-   Table detection and reconstruction\
-   Multi-language handwriting recognition\
-   Document summarization

------------------------------------------------------------------------
