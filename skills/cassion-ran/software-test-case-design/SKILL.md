# test_case_design_senior - Senior Functional Test Case Design

## Skill Overview

Possesses senior functional test engineer test case design capabilities, capable of outputting high-quality test cases with standard structure, high coverage, clear logic, and comprehensive consideration; **supports complex scenarios such as page navigation, detail page navigation, related page navigation, route parameters, page linkage, etc.**; strictly outputs according to standard templates, including complete fields such as test case ID, test type, functional module, sub-function, test title, case level, preconditions, test steps, expected results, actual results, etc., meeting enterprise-level testing standards and quality requirements.

---

## Core Capabilities

### 1. Standard Test Case Structure Output
- **Strictly follow the complete field template (strictly output test cases according to the output template)**
  - Test Case ID: Unique identifier for tracking and management
  - Test Type: Functional testing, performance testing, security testing, compatibility testing, etc.
  - Functional Module: Business module or system component to which it belongs
  - Sub-function: Specific function point or operation scenario
  - Test Title: Concisely describe the test purpose
  - Case Level: P0 (Critical), P1 (Important), P2 (General), P3 (Optional)
  - Preconditions: Status or data preparation that must be met before executing the test
  - Test Steps: Detailed operation steps to ensure repeatable execution
  - Expected Results: Expected output or status change for each step
  - Actual Results: Actual result record after test execution

### 2. Deep Requirement Breakdown and Test Point Extraction
- **Identify explicit test points**: Functional specifications directly obtained from requirement documents, UI designs, flowcharts, interface documents, code, and other software development-related documents
- **Mine implicit test points**: User behavior patterns and exception scenarios derived based on experience
- **Ensure full coverage**: Functional integrity verification, data correctness verification, interface consistency verification
- **Priority classification**: Determine testing priorities based on business importance and risk level

### 3. High Coverage Test Case Design
- **Main flow test cases**: Normal user operation process verification
- **Branch flow test cases**: Coverage of various conditional branch paths
- **Exception scenario test cases**: Error input, abnormal operation, system failure handling
- **Boundary value test cases**: Input range boundaries, quantity boundaries, time boundaries
- **Exception parameter test cases**: Special characters, ultra-long strings, illegal formats
- **Permission verification test cases**: Different role permission isolation and access control
- **Data consistency test cases**: Data cross-module synchronization, transaction consistency
- **Concurrency scenario test cases**: Multiple people operating simultaneously, data race detection

### 4. Rigorous and Clear Test Case Logic
- **Steps are concise and executable**: Avoid ambiguous descriptions, each step can be independently verified
- **Expected results are clear and unambiguous**: Use objective and measurable expressions, not subjective judgments
- **Strong readability**: Structured presentation for quick understanding of test intent
- **Strong reusability**: General scenarios can be abstracted into test suites, supporting batch calls

### 5. Application of Advanced Test Case Design Methods
- **Equivalence partitioning**: Divide input domain into valid/invalid equivalence classes to reduce redundant test cases
- **Boundary value analysis**: Design special tests for boundary situations to find common errors
- **Scenario method**: Build end-to-end test scenarios based on user business processes
- **Decision table driven**: Multi-condition combination scenarios, exhaust all possibilities
- **Error guessing**: Predict potential problems based on historical defect data and development experience
- **Risk-driven testing**: Prioritize coverage of high-risk areas and high-frequency usage scenarios

### 6. Complex Business Scenario Coverage
- **Cross-module integration testing**: Collaboration verification between multiple systems/modules
- **Upstream and downstream dependency testing**: Data source, external interface, message queue and other dependency verification
- **Interface linkage testing**: REST API, GraphQL, WebSocket and other multi-protocol interface coordination
- **Exception fallback testing**: Effectiveness verification of service degradation, circuit breaking, retry mechanisms
- **Reverse operation testing**: Correct handling of undo, rollback, compensation operations

### 7. Test Case Standardization and Implementability
- **Unified format**: Table or document format conforming to enterprise specifications
- **Complete fields**: No missing required information, complete metadata
- **Strong executability**: Directly used for manual testing or automated script generation
- **Regression friendly**: Easy to maintain and update, supporting version iteration
- **Automation docking**: Steps can be mapped to test code, expected results can be asserted
- **Quality assessment support**: Coverage metrics can be quantified, defect density can be counted

### 8. Page Navigation and Route Testing
- **Page navigation testing**: Button navigation, list to detail page, menu navigation, external link navigation
- **Detail page navigation testing**: Click from list page to enter detail page, verify data display integrity
- **Related page navigation**: Navigate from current page to business-related page (e.g., order→user, product→store)
- **Route parameter testing**: URL parameter passing, query parameters, path parameters, parameter missing/error handling
- **Navigation permission verification**: Unlogged navigation to login page, no permission navigation to 403, unauthorized access interception
- **Navigation back/return testing**: Browser back, return button, breadcrumb navigation, history stack management
- **Exception navigation testing**: 404 page, empty data page, error parameter navigation, loop navigation detection

### 9. Post-Navigation Page Verification
- **Page rendering verification**: Complete page elements, correct layout, no misalignment/missing
- **Data loading verification**: Detail data consistent with list, correct data format, empty state handling
- **Title matching verification**: Page title matches content, dynamic title update correctly
- **Parameter passing verification**: Route parameters correctly passed to target page, parameter parsing without error
- **Page status verification**: Loading status, success status, error status, empty status displayed correctly
- **Interaction function verification**: Buttons, forms, Tab switching and other functions in detail page work normally

### 10. Cross-Page Linkage Logic
- **Multi-page business association**: Analyze business process relationships between pages, design end-to-end tests
- **Data passing testing**: Data passing between pages, form data carrying, state sharing
- **State synchronization testing**: After an operation on one page, related page state updates synchronously
- **Cache consistency**: Whether data is refreshed after page return, cache strategy verification
- **Message notification linkage**: Operation triggers notification, notification click navigates to correct page

---

## Output Template

### Test Case Excel/Table Format

| Test Case ID | Test Type | Functional Module | Sub-function | Test Title | Case Level | Preconditions | Test Steps | Expected Results | Actual Results |
|------------|---------|---------|--------|---------|---------|---------|---------|---------|---------|
| TC_XXX_001 | Functional Test | User Management | Login | Verify that correct username and password can log in successfully | P0 | 1. User has registered<br>2. Network is normal | 1. Open login page<br>2. Enter correct username<br>3. Enter correct password<br>4. Click login button | 1. Navigate to homepage<br>2. Display user information | Pending execution |

### Test Case ID Rules

`TC_{ModuleAbbreviation}_{FunctionSequenceNumber}_{ScenarioSuffix}`

Examples:
- `TC_USER_LOGIN_001_NORMAL` - User Module - Login Function - Item 001 - Normal Scenario
- `TC_ORDER_DETAIL_002_JUMP` - Order Module - Detail Page - Item 002 - Navigation Scenario
- `TC_PRODUCT_LINK_003_CROSS` - Product Module - Related Page - Item 003 - Cross-Page Linkage

### Case Level Definition

| Level | Description | Applicable Scenarios |
|-----|------|---------|
| P0 | Critical Cases | Core business processes, problems that prevent system normal use, main process navigation |
| P1 | Important Cases | Main functions, problems affecting user experience, detail page navigation, permission verification |
| P2 | General Cases | Secondary functions, problems that do not affect main process, related page navigation |
| P3 | Optional Cases | Edge scenarios, beautification/optimization related, exception parameter navigation |

### Test Type Classification

- **Functional Testing**: Verify whether functions meet requirements
- **Performance Testing**: Response time, throughput, resource occupation
- **Security Testing**: Authentication, authorization, data encryption, XSS/SQL injection
- **Compatibility Testing**: Browser, operating system, device resolution
- **Regression Testing**: Verify original functions are not damaged after modification
- **Interface Testing**: API contract, data transmission, error handling
- **UI Testing**: Interface layout, interaction experience, copy accuracy
- **Route Testing**: Page navigation, route parameters, URL standards, browser history
- **Linkage Testing**: Cross-page data passing, state synchronization, business association

---

## Usage Methods

### Trigger Scenarios

This skill automatically activates when users provide the following types of requests:

1. **Generate/write test cases**: "Help me write test cases for the user login function"
2. **Improve test cases**: "These test cases are not comprehensive enough, please add exception scenarios"
3. **Review test cases**: "Check if these test cases have any omissions"
4. **Convert format**: "Convert the requirements in Word to test cases"
5. **Supplement coverage**: "What test scenarios are missing for this payment function"
6. **Review assistance**: "I need to prepare for test case review, generate a complete set of test cases"
7. **Page navigation testing**: "Help me design test cases for list to detail page navigation"
8. **Route parameter testing**: "This page URL has parameters, how to test"
9. **Cross-page linkage**: "Order page and user page are related, how to design test cases"

### Input Elements

To generate high-quality test cases, provide the following information as much as possible:

1. **Requirement Description**: Detailed description of functional requirements
2. **Business Background**: Positioning of the function in the overall product
3. **Constraints**: Technical limitations, compliance requirements, etc.
4. **Target Users**: Main user groups and their characteristics
5. **Related Systems**: Other modules or third-party services involved
6. **Page Route Information**: URL structure, route parameters, navigation logic
7. **Page Association Relationships**: Business associations between pages, data flow

### Output Content

1. **Complete Test Case Set**: Cover all identified test points
2. **Test Priority Sorting**: Display by P0-P3 classification
3. **Coverage Description**: List of covered test dimensions
4. **Missing Risk Tips**: Suggestions for possible test blind spots
5. **Page Navigation Special Description**: Navigation path, parameter verification, permission check
6. **Linkage Scenario Description**: Cross-page data flow, state synchronization points

---

## Best Practices

### Test Case Design Principles

✅ **DO - Recommended Practices**
- Each test case verifies only one clear objective
- Use clear numerical sequence numbers to mark steps
- Expected results use deterministic words such as "should/must/will"
- Include verification of both forward and reverse situations
- Mark desensitization processing methods for sensitive information
- Add screenshots or pseudocode instructions for complex scenarios
- Page navigation cases clearly mark the navigation target page
- Route parameter cases cover parameter missing, error, and out-of-bounds scenarios
- Linkage cases mark data passing paths and synchronization points

❌ **DON'T - Practices to Avoid**
- Vague descriptions such as "check if it works normally"
- Execute too many unrelated operations at once
- Ignore preconditions and environment configuration
- Mix multiple verification points in one step
- Use subjective judgments instead of objective measurements
- Ignore exception handling processes
- Ignore page status verification after navigation
- Ignore security verification of route parameters
- Ignore cross-page data consistency issues

### Test Case Review Points

1. **Completeness Check**: Whether all requirement points and implicit scenarios are covered
2. **Independence Check**: Whether there are strong dependencies between test cases
3. **Executability Check**: Whether steps are clear and tools are available
4. **Maintainability Check**: Naming standards, changes are traceable
5. **Priority Rationality**: Whether P0 test cases are truly critical
6. **Navigation Coverage Check**: Whether page navigation paths are fully covered
7. **Parameter Verification Check**: Whether route parameter testing is sufficient
8. **Linkage Logic Check**: Whether cross-page data flow is clear

### Test Case Management Suggestions

- Establish test case library version management mechanism
- Regularly clean up expired or obsolete test cases
- Continuously optimize test cases based on defect feedback
- Reuse test cases combined with automated testing frameworks
- Maintain the correlation between test cases and requirement versions
- Maintain route mapping tables for page navigation test cases
- Maintain page dependency diagrams for linkage test cases

---

## Example Cases

### Example 1: E-commerce Order Placement Function Test Case

```markdown
## Order Module - Product Order Placement - P0

### TC_ORDER_CREATE_001 Normal Order Placement Process

**Test Type**: Functional Test  
**Functional Module**: Order Management  
**Sub-function**: Product Order Placement  
**Case Level**: P0  
**Preconditions**: 
1. User has logged in and account balance is sufficient
2. Product inventory is greater than 0
3. Shipping address has been configured

**Test Steps**:
1. Browse product detail page
2. Select specification model (if any)
3. Click "Place Order Now" button
4. Confirm order information (product, quantity, price, shipping address)
5. Select payment method
6. Click "Submit Order" button
7. Complete payment

**Expected Results**:
1. Enter order confirmation page
2. Order amount calculation is accurate (including shipping and discounts)
3. Order created successfully, return order number
4. Inventory deduction is correct
5. Receive order confirmation notification

**Actual Results**: Pending execution
```

### Example 2: User Registration Function Exception Scenario

```markdown
## User Module - Registration - P1

### TC_USER_REGISTER_002 Email Format Error

**Test Type**: Functional Test  
**Functional Module**: User Management  
**Sub-function**: User Registration  
**Case Level**: P1  
**Preconditions**: Access registration page

**Test Steps**:
1. Enter incomplete format email in email input box (e.g., abc@com)
2. Enter legal password and confirm password
3. Click "Register" button

**Expected Results**:
1. Email field displays red error prompt
2. Prompt content clearly informs format requirements
3. Cannot continue to submit form
4. No error logs in console

**Actual Results**: Pending execution
```

### Example 3: List to Detail Page Navigation Test

```markdown
## Product Module - List to Detail - P0

### TC_PRODUCT_LIST_001 Normal Navigation to Detail Page

**Test Type**: Route Test  
**Functional Module**: Product Management  
**Sub-function**: List to Detail Navigation  
**Case Level**: P0  
**Preconditions**: 
1. User has logged in
2. Product list page has data

**Test Steps**:
1. Open product list page
2. Click any product card/name
3. Wait for page navigation to complete
4. Verify detail page display content

**Expected Results**:
1. Successfully navigate to product detail page
2. URL contains correct product ID (e.g., /product/12345)
3. Product information displayed in detail page is consistent with list
4. Product image, price, inventory and other key information are correct
5. Detail page function buttons (purchase, favorite, etc.) are available

**Actual Results**: Pending execution
```

### Example 4: Route Parameter Test

```markdown
## Order Module - Detail Page - P1

### TC_ORDER_DETAIL_002 Route Parameter Missing

**Test Type**: Route Test  
**Functional Module**: Order Management  
**Sub-function**: Detail Page Route  
**Case Level**: P1  
**Preconditions**: User has logged in

**Test Steps**:
1. Manually access order detail page URL, but omit order ID parameter (e.g., /order/detail?id=)
2. Observe page response

**Expected Results**:
1. Page displays error prompt "Order ID cannot be empty"
2. Or automatically navigate to order list page
3. No white screen or system error occurs

**Actual Results**: Pending execution

---

### TC_ORDER_DETAIL_003 Route Parameter Illegal

**Test Type**: Security Test  
**Functional Module**: Order Management  
**Sub-function**: Detail Page Route  
**Case Level**: P1  
**Preconditions**: User has logged in

**Test Steps**:
1. Manually access order detail page URL, pass illegal order ID (e.g., /order/detail?id=abc)
2. Observe page response

**Expected Results**:
1. Page displays "Order does not exist" or similar prompt
2. No order detail information is displayed
3. No entry for unauthorized access to other orders is provided

**Actual Results**: Pending execution
```

### Example 5: Cross-Page Linkage Test

```markdown
## Order Module - User Association - P1

### TC_ORDER_USER_001 Order Page to User Detail Page Navigation

**Test Type**: Linkage Test  
**Functional Module**: Order Management  
**Sub-function**: Related Page Navigation  
**Case Level**: P1  
**Preconditions**: 
1. User has logged in
2. Completed orders exist

**Test Steps**:
1. Open order detail page
2. Click user name/avatar in buyer information area
3. Wait for page navigation
4. Verify navigation target page

**Expected Results**:
1. Successfully navigate to user detail/store page
2. User information is consistent with buyer information in order
3. URL contains correct user ID
4. User page functions work normally (follow, send message, etc.)

**Actual Results**: Pending execution

---

## Order Module - State Synchronization - P1

### TC_ORDER_USER_002 Order Status Change List Synchronization

**Test Type**: Linkage Test  
**Functional Module**: Order Management  
**Sub-function**: State Synchronization  
**Case Level**: P1  
**Preconditions**: 
1. User has logged in
2. Orders awaiting shipment exist

**Test Steps**:
1. Open order list page, record order status
2. Click to enter order detail page
3. Execute shipment operation in detail page
4. Return to list page (browser back or click breadcrumb)
5. Check order status in order list

**Expected Results**:
1. Order status in list page has been updated to "Shipped"
2. Or page prompts to refresh and display latest status
3. Data is consistent with detail page operation result

**Actual Results**: Pending execution
```

### Example 6: Permission Navigation Test

```markdown
## System Module - Permission Control - P0

### TC_SYS_AUTH_001 Unlogged Access to Detail Page

**Test Type**: Security Test  
**Functional Module**: Permission Management  
**Sub-function**: Login Interception  
**Case Level**: P0  
**Preconditions**: User not logged in

**Test Steps**:
1. Directly access detail page URL requiring login (e.g., /order/detail?id=123)
2. Observe page navigation

**Expected Results**:
1. Automatically navigate to login page
2. After successful login, can return to original access page (with redirect parameter)
3. No order information is leaked

**Actual Results**: Pending execution

---

### TC_SYS_AUTH_002 Unauthorized Access to Others' Orders

**Test Type**: Security Test  
**Functional Module**: Permission Management  
**Sub-function**: Unauthorized Access  
**Case Level**: P0  
**Preconditions**: User A has logged in

**Test Steps**:
1. Obtain User B's order ID
2. User A accesses User B's order detail page (/order/detail?id=User B's Order ID)
3. Observe page response

**Expected Results**:
1. Display "No access permission" or "Order does not exist"
2. No User B's order information is displayed
3. Security log is recorded

**Actual Results**: Pending execution
```

### Example 7: Browser Back Test

```markdown
## General Module - Browser History - P2

### TC_BROWSER_BACK_001 Detail Page Return to List

**Test Type**: Route Test  
**Functional Module**: Browser History Management  
**Sub-function**: Back Function  
**Case Level**: P2  
**Preconditions**: 
1. User is on product list page
2. List has pagination or filter conditions

**Test Steps**:
1. Set filter conditions on list page (e.g., price range, brand)
2. Click a product to enter detail page
3. Use browser back button to return
4. Check list page status

**Expected Results**:
1. Return to list page instead of homepage
2. Previous filter conditions are maintained
3. Scroll position is maintained or reasonably reset
4. List data is not lost

**Actual Results**: Pending execution
```

---

## Quality Assurance Standards

### Test Case Review Pass Standards

1. ✅ **Coverage Standard Met**: Core function P0 test case coverage 100%
2. ✅ **Logic Self-consistent**: No contradictory or conflicting step descriptions
3. ✅ **Executability**: Single test case verification can be completed within 3 minutes
4. ✅ **Boundary Coverage**: Input boundaries and exception scenarios have corresponding test cases
5. ✅ **Priority Rational**: P0 test cases do not exceed 30% of total
6. ✅ **Navigation Coverage**: Page navigation scenarios fully covered
7. ✅ **Parameter Verification**: Route parameter testing is complete
8. ✅ **Linkage Complete**: Cross-page data flow testing is clear

### Delivery Quality Standards

- Total number of test cases not less than 3 times the number of requirement points (including exception scenarios)
- P0+P1 test case proportion not less than 60%
- Average number of steps per test case is 3-8 steps
- No empty descriptions, expected results can be objectively verified
- Conform to enterprise testing management specification format requirements
- Page navigation test cases include navigation target, parameters, permission verification
- Linkage test cases include data passing path and synchronization point description

---

## Technical Support

### Common Test Method Quick Reference

**Equivalence Partitioning Examples**:
- Age input box: Valid equivalence class [1,120], invalid equivalence class <1, >120, non-numeric
- Status dropdown: Valid equivalence class [Enabled, Disabled, Frozen], invalid equivalence class any other value
- **Route parameters**: Valid equivalence class [legal ID format], invalid equivalence class [empty value, non-numeric, ultra-long, special characters]

**Boundary Value Analysis Examples**:
- File upload size limit 10MB: 9MB, 10MB, 10.1MB
- Text box limit 200 characters: 199 characters, 200 characters, 201 characters
- **List pagination**: Page 1, last page, beyond maximum page number

**Decision Table Example**:
| Condition | A(Has Coupon) | B(Over 100 Yuan) | C(Available) | Result |
|-----|-----------|----------|-------|-----|
| 1 | Y | Y | Y | Can use |
| 2 | Y | Y | N | Cannot use (expired) |
| 3 | Y | N | Y | Cannot use (threshold not met) |
| 4 | N | Y/Y | Y/Y | Not applicable |

### Page Navigation Test Checklist

- [ ] Normal navigation: Click navigation target is correct
- [ ] Parameter passing: URL parameters are complete and correct
- [ ] Permission verification: Unlogged/no permission interception is correct
- [ ] 404 handling: Non-existent resources navigate to 404 page
- [ ] Empty state: Display empty state page when no data
- [ ] Browser back: History stack management is correct
- [ ] Return button: In-page return function works normally
- [ ] Breadcrumb navigation: Hierarchical navigation is accurate
- [ ] External navigation: Open external links in new tab
- [ ] Loop navigation: Detect and prevent loop redirection

### Cross-Page Linkage Test Checklist

- [ ] Data passing: Data carrying between pages is correct
- [ ] State synchronization: Related page state updates after operation
- [ ] Cache strategy: Return page data refresh strategy is reasonable
- [ ] Message notification: Notification click navigates to correct page
- [ ] Business closed loop: Cross-page business process is complete
- [ ] Data consistency: Multiple pages displaying same data are consistent
- [ ] Operation feedback: Operation on one page, related page has feedback

---

## Appendix

### Common Test Data Types

| Data Type | Valid Range | Typical Boundaries | Exception Examples |
|---------|---------|---------|---------|
| Integer | -2147483648 to 2147483647 | -1, 0, 1, max value, max+1 | Decimal, letters |
| Float | According to precision requirements | 0.0, 0.1, minimum positive number | Infinity, NaN |
| String | 1-200 characters | 0 characters, 200 characters, 201 characters | null, emoji, special symbols |
| Date | 1970-01-01 to 2099-12-31 | Previous day, current day, next day | Future year, illegal date |
| Boolean | true/false | - | 1, 0, "true", "" |
| Enum | predefined values | First item, last item, middle item | Values not in defined range |
| **Route Parameter** | Conforms to URL standards | Normal ID, empty value, boundary value | Special characters, SQL injection, XSS |

### Reference Resources

- ISTQB Testing Terminology Standard
- ISO/IEC/IEEE 29119 Software Testing Standard
- Google Testing Blog
- Microsoft Test Engineering Guidelines
- Web Route Testing Best Practices
- Frontend Page Linkage Testing Guide
