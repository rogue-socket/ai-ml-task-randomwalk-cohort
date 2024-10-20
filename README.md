# OCR Image Grouping and Subgrouping

This Python script processes an image using Optical Character Recognition (OCR) via the `pytesseract` library. It identifies text blocks from the image, groups them based on proximity and formatting, classifies them into headings and subtexts, and orders them correctly. The grouped and sorted text is then output in a structured manner.

## Prerequisites

### 1. Tesseract-OCR:
- You need to have Tesseract installed on your machine.  
  [Download Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
- Update the `pytesseract.pytesseract.tesseract_cmd` line in the script to point to the Tesseract executable on your machine.

### 2. Python Libraries:
- `pytesseract`: For Optical Character Recognition (OCR)
- `Pillow (PIL)`: For image processing
- `collections.defaultdict`: To manage graph structures
- `re`: For regular expression operations

You can install the required Python libraries using the following command:

```bash
pip install pytesseract Pillow
```

### 3. Run File:
- run the file `f1_part2.py` by changing the location of the image and also the loaction of pytesseract
- run the file `f1.ipynb` to see the outputs of the image given in the readme(indian flag)
- `f1_part2.ipynb` was adaptation of `f1.ipynb` to the sample image given, the hormones diagram
- final code to be run is in `f1_part2.py`
