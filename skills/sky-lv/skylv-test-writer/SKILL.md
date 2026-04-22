---
name: skylv-test-writer
slug: skylv-test-writer
version: 1.0.0
description: "Auto-generates unit tests and integration tests from source code. Supports Jest, Pytest, Mocha. Triggers: write tests, generate tests, unit test, test coverage, testing scaffold."
author: SKY-lv
license: MIT
tags: [testing, jest, pytest, unit-test]
keywords: [testing, unit-test, integration-test, jest, pytest, mocha]
triggers: write tests, generate tests, test coverage
---

# Test Writer

## Overview
Analyzes source code and auto-generates comprehensive unit and integration tests.

## When to Use
- User asks to "write tests" or "add test coverage"
- User wants to "test this function"

## How It Works

### Step 1: Detect test framework

Check: package.json (jest/mocha), pytest.ini, pyproject.toml, conftest.py

### Step 2: Parse source

Read source files. Identify: function signatures, parameters, return types, error handling, edge cases.

### Step 3: Generate test cases

For each function generate: happy path, edge cases (empty/null/zero), error cases, boundary cases.

### Step 4: Write test file

JavaScript: __tests__/filename.test.js or filename.test.js
Python: tests/test_filename.py

## Templates

### Jest
describe('functionName', () => {
  test('should return expected result', () => {
    expect(functionName(input)).toBe(expected);
  });
  test('should throw for invalid input', () => {
    expect(() => functionName(invalid)).toThrow();
  });
});

### Pytest
def test_function_normal():
    assert function_name(input) == expected

def test_function_invalid():
    with pytest.raises(ErrorType):
        function_name(invalid)

## Tips
- Target 80%+ coverage on critical functions
- Cover all branches and error paths
- Mock external dependencies (API, filesystem, DB)