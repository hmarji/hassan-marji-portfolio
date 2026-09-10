/* HM Portfolio — Life Timeline metadata
Edit only the date and caption values below.

Examples:
  date: "1978"
  date: "June 1996"
  caption: "At school in Beirut."

The file name identifies the photograph, so you can reorder thumbnails
without losing the correct date/caption.
*/
window.HM_LIFE_TIMELINE = [
  { file: "21.webp", date: "", caption: "" },
  { file: "22.webp", date: "", caption: "" },
  { file: "23.webp", date: "", caption: "" },
  { file: "24.webp", date: "", caption: "" },
  { file: "25.webp", date: "", caption: "" },
  { file: "26.webp", date: "", caption: "" },
  { file: "27.webp", date: "", caption: "" },
  { file: "28.webp", date: "", caption: "" },
  { file: "29.webp", date: "", caption: "" },
  { file: "30.webp", date: "", caption: "" },
  { file: "31.webp", date: "", caption: "" },
  { file: "32.webp", date: "", caption: "" },
  { file: "33.webp", date: "", caption: "" },
  { file: "34.webp", date: "", caption: "" },
  { file: "35.webp", date: "", caption: "" },
  { file: "36.webp", date: "", caption: "" },
  { file: "37.webp", date: "", caption: "" },
  { file: "38.webp", date: "", caption: "" },
  { file: "39.webp", date: "", caption: "" }
];

/* HM Portfolio — Life Timeline temporarily hidden.
   Keep the complete timeline system in the project for future use.
   To restore it later, remove only this block. */
(() => {
  const hideTimeline = () => {
    const timeline = document.querySelector('.life-timeline');
    if (!timeline) return;
    timeline.hidden = true;
    timeline.setAttribute('aria-hidden', 'true');
    timeline.style.setProperty('display', 'none', 'important');
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', hideTimeline, { once: true });
  } else {
    hideTimeline();
  }
})();
