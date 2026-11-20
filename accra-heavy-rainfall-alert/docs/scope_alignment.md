# Scope alignment: approved proposal against the delivered project

Fill the Evidence column with real screenshots, file paths or commit links. Change a status only if it is true.

| Planned feature | Intended purpose | Status | Evidence |
|---|---|---|---|
| Prepare HDX rainfall data for Greater Accra | Training inputs | Completed | Notebook sections 1 to 2 |
| Flood labels from real flood records | Train on real floods | Not implemented. No flood records were available | Replaced by the heavy-rain stand-in (above 58.4 mm); notebook section 4 |
| Neighborhood-level prediction (Odawna basin, Ashaiman) | Local early warning | Not implemented. The open data is region-level | Notebook section 2 |
| Random Forest and XGBoost comparison | Choose the best model | Partial. Four models on one split; Random Forest and logistic regression, with and without SMOTE, over five windows | Notebook sections 6 and 7 |
| Class-imbalance handling (SMOTE) | Cope with rare heavy-rain periods | Completed, used only inside training folds | Notebook section 7 |
| Targets of AUC 0.80 and recall 75% | Judge the model | Changed to PR-AUC and AUC against a calendar-only baseline, because a month lookup already scores about 0.82 AUC | Notebook sections 5 and 7 |
| Feature importance | Explain predictions | Completed (permutation importance in the notebook, model importance in the dashboard) | Notebook section 11; dashboard "Show details" |
| Dashboard for NADMO officials | Show risk | [Completed / Partial: fill in after you run it] | [screenshots in docs/screenshots] |
| "Real-time" updates | Continuous warning | Partial. Data comes in 10-day periods and the prototype has no live feed | About page of the dashboard |
| Backend API | Serve predictions | [Completed / Partial: fill in after you run it] | `api/main.py`, `/docs` screenshot |
| SQLite prediction history | Store results | Not implemented. Files are used instead | `models/`, `data/processed/` |
| Software testing | Check the code | [fill in: test types, counts and results] | `docs/testing.md` |
| User testing with NADMO officials | Check usefulness | Not done. No participants; outside the ethics clearance | Clearance letter |
| NADMO and GMet data | Richer data | Not obtained | None |
