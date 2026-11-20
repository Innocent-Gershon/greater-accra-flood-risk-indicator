# Fairness and limitations

- **Stand-in target.** Heavy rain is not a flood. Two of four documented floods (June 2015 and June 2026) were rated
  High and followed by heavy rain. March 2023 had 54.8 mm of rain, just under the cut-off, and was rated Low.
  October 2023 had no heavy period and was rated Typical. Four events are too few to give a hit rate.
- **Coarse data.** The data is a region-wide satellite average. It smooths out local downpours and cannot show
  conditions in a single neighborhood. A validation study of satellite rainfall products in Ghana and Zambia reported
  poor detection of heavy rain events [add the citation: arXiv 2501.14829, with authors from Zotero].
- **Season.** The bands mostly follow the season: 204 of the 271 High periods in the test windows fall in May and June.
  The model beat a calendar-only lookup in all five windows, but only by a small margin.
- **A Low band is not safe.** 27 of 812 Low periods (3.3%) were still followed by heavy rain. The dashboard shows the past
  rate beside every band and never uses the word "safe".
- **Few events.** About 10% of periods are heavy, so each test window had only 24 to 36 heavy periods.
- **Who is left out.** The tool is built for disaster management officials. Residents are not direct users, and the
  dashboard needs an internet connection. A phone check is recorded in `docs/testing.md`.
- **Bias risk.** Using one region-wide average can hide areas that get different rain. Neighborhood-level data, flood records,
  elevation and land cover are the recommended next steps.
