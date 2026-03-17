# Brain-Scroller

Design:

**app.py**: 
UI Made using Flask. Uses articles.json and the list of json files, which will continue to grow using processor.py

**articles.json**: 
The various article topic categories. This will eventually be used to customize user experience, allowing them to filter content.

**processor.py**: 
Takes in a research paper PDF, extracts all images/figures from the research papers, chooses a few interesting images/figures and generates captions: content to be associated with the visual in a post, generally offering context and summarizing a piece of the overall paper message. Has to be updated with new path defined each time it gets run.

**test-processor.py**:
Prior to running processor.py, run test-processor.py to make sure there are images to extract from the pdf, otherwise processor.py won't work.

**____.json**: 
File generated (either by processor.py or manually) using the following format:
[
  {
    "post_id": "GlacierDetachment_RemoteSensing",
    "article_id": "GlacialDetachment",
    "pages": [
      {
        "image": "glaciers/fig_5_0.jpeg",
        "figure": "Tracking Glacier Detachments from Space",
        "caption": "When massive glacier detachments occur unwitnessed, scientists turn to remote sensing to reconstruct the events. This sequence of satellite images shows Flat Creek Glacier before and after its 2013 detachment. The red line marks the initial detachment, revealing how the glacier front advanced and accumulated ice debris in the following months, providing crucial insights into the event's aftermath."
      },
      {
        "image": "glaciers/fig_7_0.jpeg",
        "figure": "Mapping Changes with Digital Elevation Models (DEMs)",
        "caption": "Digital Elevation Models (DEMs) are powerful tools for quantifying landscape changes. By subtracting a pre-detachment DEM from a post-detachment one, scientists create a 'dH map' (difference in height). This map (Fig. S3) clearly shows areas of erosion (blue) where ice detached and deposition (red) where debris accumulated, allowing researchers to precisely measure the volumetric impact of these events. Table 2 (within the same image context) further quantifies these massive changes, showing millions of cubic meters of ice and debris moved."
      }
    ]
  }
]
