# Combine Two Tables

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** Database
- **Link:** https://leetcode.com/problems/combine-two-tables/
- **Language (detected):** mysql
- **Runtime:** 431 ms
- **Memory:** 0B

## Problem (summary)

Table: Person

+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| personId    | int     |
| lastName    | varchar |
| firstName   | varchar |
+-------------+---------+
personId is the primary key (column with unique values) for this table.
This table contains information about the ID of some persons and their first and last names.

 

Table: Address

+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| addressId   | int     |
| personId    | int     |
| city        | varchar |
| state       | varchar |
+-------------+---------+
addressId is the primary key (column with unique values) for this table.
Each row of this table contains information about the city and state of one person with ID = PersonId.

 

Write a solution to report the first name, last name, city, and state of each person in the Person table. If the address of a personId is not present in the Address table, report null instead.

Return the result table in any order.

The result format is in the following example.

 

Example 1:

Input: 
Person table:
+----------+----------+-----------+
| personId | lastName | firstName |
+----------+----------+-----------+
| 1

(Truncated.)

## Approach

**Approach**

We need to combine the information from the `Person` table with the optional address information from the `Address` table. The natural way to do this in SQL is a **LEFT JOIN**:

```sql
SELECT p.firstName,
       p.lastName,
       a.city,
       a.state
FROM   Person AS p
LEFT   JOIN Address AS a
       ON p.personId = a.personId;
```

* The `LEFT JOIN` keeps every row from `Person`.
* When a matching `personId` exists in `Address`, the corresponding `city` and `state` are returned.
* If no match exists, the columns from `Address` are `NULL`, which satisfies the requirement to report `null` for missing addresses.

The query returns the columns in the order required by the problem statement. The result can be in any order, so no additional `ORDER BY` clause is needed.

## Complexity

- **Time:** O(N + M) – the database scans the `Person` table (size N) and the `Address` table (size M) once to build the join.
- **Space:** O(N + M) – the join materialises a result set that, in the worst case, contains one row per person (plus extra rows if a person has multiple addresses).

## Pros

- Very concise – a single SQL statement solves the problem.
- Uses a standard LEFT JOIN, which is well‑optimized in relational engines.
- Handles missing addresses automatically via NULL values.
- Works regardless of the order of rows in the input tables.

## Cons

- If the `Address` table contains multiple rows for the same `personId`, the query will produce duplicate rows for that person (the problem assumes at most one address per person).
- Relies on the database’s join algorithm; extremely large tables may need indexes on `personId` for optimal performance.

## Edge cases

- `Person` table is empty – the query returns an empty result set.
- `Address` table is empty – every person gets `NULL` for `city` and `state`.
- A person has no matching address – `city` and `state` are `NULL` as required.
- An address exists for a `personId` that is not present in `Person` – such rows are ignored by the LEFT JOIN.
