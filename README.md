# moodle_log_anonymizer

Python script for anonymizing the logs provided by Moodle, changing the students names to random ones (but keeping the same name for the same student) and removing the access origin and IP columns

## Usage

You can run the script with python 3.9 passing the path to the logs to be anonymized and the path for the result to be saved to:

```bash
python anonymizer.py moodle_logs.csv anonymized_moodle_logs.csv
```

## Testing

The tests reside on the `anonymizer_test.py` file and use the `unittest` package, to run them execute:

```bash
python -m anonymizer_test
```

## References

Based on the implementation of [anonymoodle](https://github.com/alfonsodelavega/anonymoodle), which works on a slightly different log structure with another language.
