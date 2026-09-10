/* HM Portfolio — Life Timeline metadata
   Written automatically by EDIT_TIMELINE.bat.
   Date format: YYYY, YYYY-MM, or YYYY-MM-DD.
*/
window.HM_LIFE_TIMELINE = [
  {
    "file": "21.webp",
    "date": "1978",
    "caption": ""
  },
  {
    "file": "22.webp",
    "date": "1979",
    "caption": ""
  },
  {
    "file": "23.webp",
    "date": "1980",
    "caption": ""
  },
  {
    "file": "24.webp",
    "date": "1981",
    "caption": ""
  },
  {
    "file": "25.webp",
    "date": "1992",
    "caption": ""
  },
  {
    "file": "26.webp",
    "date": "1992",
    "caption": ""
  },
  {
    "file": "27.webp",
    "date": "2007",
    "caption": ""
  },
  {
    "file": "28.webp",
    "date": "2008",
    "caption": ""
  },
  {
    "file": "29.webp",
    "date": "2009",
    "caption": ""
  },
  {
    "file": "30.webp",
    "date": "2010",
    "caption": ""
  },
  {
    "file": "31.webp",
    "date": "2011",
    "caption": ""
  },
  {
    "file": "32.webp",
    "date": "2012",
    "caption": ""
  },
  {
    "file": "33.webp",
    "date": "2012",
    "caption": ""
  },
  {
    "file": "34.webp",
    "date": "2012",
    "caption": ""
  },
  {
    "file": "35.webp",
    "date": "2013",
    "caption": ""
  },
  {
    "file": "36.webp",
    "date": "2012",
    "caption": ""
  },
  {
    "file": "37.webp",
    "date": "2018",
    "caption": ""
  },
  {
    "file": "38.webp",
    "date": "2019",
    "caption": ""
  },
  {
    "file": "39.webp",
    "date": "2019",
    "caption": ""
  }
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
