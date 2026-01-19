# Create Hello World Function

- **Platform:** LeetCode
- **Difficulty:** Easy
- **Tags:** 
- **Link:** https://leetcode.com/problems/create-hello-world-function/
- **Language (detected):** javascript
- **Runtime:** 44 ms
- **Memory:** 53.1 MB

## Problem (summary)

Write a function createHelloWorld. It should return a new function that always returns "Hello World".
 

Example 1:

Input: args = []
Output: "Hello World"
Explanation:
const f = createHelloWorld();
f(); // "Hello World"

The function returned by createHelloWorld should always return "Hello World".

Example 2:

Input: args = [{},null,42]
Output: "Hello World"
Explanation:
const f = createHelloWorld();
f({}, null, 42); // "Hello World"

Any arguments could be passed to the function but it should still always return "Hello World".

 

Constraints:

	- 0

## Approach

The solution defines a higher‑order function `createHelloWorld` that returns a new inner function. The inner function uses the rest parameter `...args` to accept any number of arguments, but it completely ignores them and always returns the constant string "Hello World". Because JavaScript treats functions as first‑class values, returning a function from another function is straightforward and satisfies the requirement that the returned function works with any arguments.

## Complexity

- **Time:** O(1) per call
- **Space:** O(1) additional space

## Pros

- Extremely simple and easy to understand
- Works with any number and type of arguments
- Constant time and space for each invocation
- Leverages JavaScript closures naturally

## Cons

- Creates a new function object each time `createHelloWorld` is called (minor overhead)
- No flexibility – always returns the same string, which is intentional but limits reuse

## Edge cases

- Calling the returned function with no arguments
- Calling with many arguments
- Passing `null`, `undefined`, objects, or other non‑primitive values as arguments
- Ensuring the returned value is exactly the string "Hello World" regardless of input
