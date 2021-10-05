# Moodle log anonymizer

Python script for anonymizing the logs provided by Moodle, changing the students names to random ones (but keeping the same name for the same student) and removing the access origin and IP columns.

It also optionally anonymizes the grades of the students, making sure the same real name is mapped to the same fake name on both output files. When anonymizing the grades this script assumes the name and surname columns have been merged into one full name column, which is done by another script used in our current project, the [moodle grades cleaner](https://github.com/JefersonFG/moodle-grades-cleaner). It also assumes the email column has been removed, which the grades cleaner does, so you might need to explicitly add anonymization support here if you wish.

## Dependencies

This project relies on the `pandas` module being available, as well as the `openpyxl` module necessary for writing and reading `.xlsx` files, format used by moodle when exporting the grades of students for a given course.

## Usage

You can run the script with python 3.9 passing the path to the logs to be anonymized and the path for the result to be saved to:

```bash
python anonymizer.py moodle_logs.csv anonymized_moodle_logs.csv
```

You can also optionally pass the path to the grades to be anonymized as well as the path for the result to be saved to:

```bash
python anonymizer.py moodle_logs.csv anonymized_moodle_logs.csv --source_grades_path moodle_grades.xlsx --target_grades_path anonymized_moodle_grades.xlsx
```

## Testing

The tests reside on the `anonymizer_test.py` file and use the `unittest` package, to run them execute:

```bash
python -m anonymizer_test
```

## References

Based on the implementation of [anonymoodle](https://github.com/alfonsodelavega/anonymoodle), which works on a slightly different log structure with another language.
