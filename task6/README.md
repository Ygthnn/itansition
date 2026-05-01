# Fake User Generator (SQL-based)

## Overview
This project implements a Faker-like system entirely in PostgreSQL using stored procedures.

## Main Function
generate_fake_users(locale, seed, batch_index, batch_size)

## Parameters
- locale: en_US or de_DE
- seed: ensures reproducibility
- batch_index: page number
- batch_size: number of users

## Algorithms

### Deterministic Random
Based on MD5 hashing:
seed + position → hash → numeric → [0,1]

### Normal Distribution
Box-Muller transform:
z = sqrt(-2 ln u1) cos(2πu2)

Used for:
- height
- weight

### Uniform Sphere Distribution
Latitude:
asin(2u - 1)

Longitude:
360u - 180

### Name Generation
- Variants:
  - First Last
  - First M. Last
  - Title First Last
  - Last, First

### Address Generation
Locale-specific formatting:
- US: "123 Main St, City, ZIP"
- DE: "Street 123, ZIP City"
