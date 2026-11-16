# Not Boring Movies

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** Database
- **Link:** https://leetcode.com/problems/not-boring-movies/
- **Language (detected):** mysql
- **Runtime:** 231 ms
- **Memory:** 0B

## Problem (summary)

Table: Cinema

+----------------+----------+
| Column Name    | Type     |
+----------------+----------+
| id             | int      |
| movie          | varchar  |
| description    | varchar  |
| rating         | float    |
+----------------+----------+
id is the primary key (column with unique values) for this table.
Each row contains information about the name of a movie, its genre, and its rating.
rating is a 2 decimal places float in the range [0, 10]

 

Write a solution to report the movies with an odd-numbered ID and a description that is not "boring".

Return the result table ordered by rating in descending order.

The result format is in the following example.

 

Example 1:

Input: 
Cinema table:
+----+------------+-------------+--------+
| id | movie      | description | rating |
+----+------------+-------------+--------+
| 1  | War        | great 3D    | 8.9    |
| 2  | Science    | fiction     | 8.5    |
| 3  | irish      | boring      | 6.2    |
| 4  | Ice song   | Fantacy     | 8.6    |
| 5  | House card | Interesting | 9.1    |
+----+------------+-------------+--------+
Output: 
+----+------------+-------------+--------+
| id | movie      | description | rating |
+

(Truncated.)

## Approach

**Approach**
1. **Filter rows** – Keep only records where `id` is odd (`id % 2 <> 0`).
2. **Exclude boring movies** – Discard rows whose `description` equals the literal string `"boring"`.
3. **Sort** – Return the remaining rows ordered by `rating` in descending order.

The query can be expressed in a single `SELECT` statement:
```sql
SELECT *
FROM Cinema
WHERE id % 2 <> 0            -- odd‑numbered IDs
  AND description <> 'boring' -- description is not "boring"
ORDER BY rating DESC;          -- highest rating first
```

## Complexity

- **Time:** O(N log N) – filtering is O(N) and the final ORDER BY requires sorting the filtered rows (worst‑case O(N log N)).
- **Space:** O(1) additional space – the database engine handles sorting internally.

## Pros

- Very concise – a single statement does all work
- Leverages database engine for filtering and sorting, which is usually optimized
- Easy to read and maintain

## Cons

- Relies on exact case‑sensitive match for "boring" – may miss variations like "Boring"
- If `description` can be NULL, the `<>` comparison will filter them out unintentionally
- Sorting can be expensive on very large tables without an index on `rating`

## Edge cases

- No rows satisfy both conditions → result set is empty
- All odd‑ID rows have description "boring" → empty result
- Multiple movies share the same rating – order among them is unspecified
- `description` contains leading/trailing spaces (e.g., " boring") – will not be filtered unless trimmed
- `id` values are negative or zero – `% 2` still works, but problem guarantees positive IDs
