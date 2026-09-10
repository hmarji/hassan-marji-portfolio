HM PORTFOLIO — ONE-PLACE IMAGE WORKFLOW
======================================

IMPORTANT
---------
You manage gallery images ONLY in the source folders listed below.
Never add, replace or delete gallery images manually inside images/thumbs/
or images/previews/. Those are generated automatically.

SELECTED WORK
-------------
images/selected-work/

PRACTICE
--------
images/practice/engineering/
images/practice/painting/
images/practice/photography/
images/practice/graphic-design/
images/practice/animation/
images/practice/training/

KNOWLEDGE
---------
images/knowledge/engineering/
images/knowledge/painting/
images/knowledge/photography/
images/knowledge/graphic-design/
images/knowledge/animation/
images/knowledge/training/

CANONICAL NAMES
---------------
engineering      (old: architecture)
graphic-design   (old: graphic)
training         (old: education)

NORMAL WORKFLOW
---------------
1. Add, replace or delete the ORIGINAL image in the correct source folder.
2. Double-click UPDATE_PORTFOLIO.bat.
3. The updater automatically:
   - moves any remaining legacy folders/files into canonical locations;
   - removes identical duplicate legacy originals safely;
   - preserves different files if a filename collision exists;
   - creates/updates optimized WebP thumbnails and previews;
   - rebuilds js/gallery-data.js;
   - removes unused generated gallery thumbnails/previews.
4. Open index.html locally and verify the website.
5. Run git status and review the changes.
6. When everything is correct, use PUSH_PORTFOLIO.bat.

LEGACY FOLDERS
--------------
The following are no longer source locations and should disappear after the
first normalized update:

images/originals/
images/education/
images/practice/architecture/
images/practice/graphic/

If an old copy exists there, UPDATE_PORTFOLIO.bat migrates it safely instead
of asking you to maintain two copies.

SPECIAL SITE ASSETS
-------------------
images/about/ and images/branding/ contain non-gallery website assets.
They are not part of the Practice/Knowledge add-delete workflow.

LIFE TIMELINE
-------------
The Life Timeline is currently hidden from public view and remains a separate
feature. Its files are preserved and are not removed by the gallery cleanup.
