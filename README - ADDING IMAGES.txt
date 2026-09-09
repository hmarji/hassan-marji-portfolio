HM PORTFOLIO — SIMPLE IMAGE WORKFLOW
====================================

After installing this package once, adding images is simple:

1. Copy images into the correct folder.
2. Double-click UPDATE_PORTFOLIO.bat.
3. Open index.html and check.
4. Push to GitHub when ready.

NEW FOLDERS
-----------
images/selected-work/

images/practice/engineering/
images/practice/painting/
images/practice/photography/
images/practice/graphic-design/
images/practice/animation/
images/practice/training/

images/knowledge/engineering/
images/knowledge/painting/
images/knowledge/photography/
images/knowledge/graphic-design/
images/knowledge/animation/
images/knowledge/training/

ORDER
-----
Use numbers at the beginning of filenames if you want an exact order:
01_house.jpg
02_villa.jpg
03_site.jpg

IMPORTANT
---------
- Practice still recognizes the old folders already used by the website, so existing work is not lost.
- On the first run, the current Selected Work images are copied into images/selected-work/ automatically.
- Existing flat images inside images/knowledge/ are also kept and categorized automatically.
- New images should be placed in the new category folders above.
- The updater creates/refreshes js/gallery-data.js automatically.
- If Pillow is installed, it also creates optimized WebP thumbnails and previews.
- GIF/SVG/WebP files remain in their original format.
- Deleting an image from one of the managed folders and running UPDATE_PORTFOLIO.bat removes it from that gallery.

DO NOT edit js/gallery-data.js by hand; it is generated automatically.
