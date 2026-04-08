# Task 2

This task computes a final SHA3-256 digest from the files inside `task2.zip`.

## Task steps

1. Calculate **SHA3-256** for every file from the archive
2. Represent each hash as **64 lowercase hexadecimal characters**
3. Sort hashes in ascending order by the **product of each hex digit increased by one**
4. Join the sorted hashes **without separators**
5. Concatenate the resulting string with the email in **lowercase**
6. Compute **SHA3-256** of the final string

## Files

- `task2.py` — script used to process the archive and compute the final result
- `task2.zip` — input archive

## Run

```bash
python task2.py task2.zip youremail@example.com