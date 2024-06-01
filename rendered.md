# Onboarding Guide

Welcome to the codebase! This guide will walk you through the core principles and steps taken in a recent pull request, ensuring you understand how to implement similar patches and solve issues effectively.

## Core Principles

### Understanding the Codebase
1. **Familiarize Yourself with the Code Structure**: Before making any changes, it's essential to understand the overall structure of the codebase. In this context, the modification was made in the `lib/response.js` file, which is part of the core library handling HTTP responses in Express.

2. **Identify the Function and Its Purpose**: The function modified in this patch is `res.clearCookie`. This function is used to clear cookies by setting their expiration date to a past date.

### Making the Change
1. **Recognize the Issue**: The issue addressed was the presence of the `maxAge` option when clearing a cookie. The `maxAge` property should be ignored when clearing cookies because setting `expires` to a past date is sufficient.

2. **Implement the Fix**: The fix involves deleting the `maxAge` property from the options object before it is used to clear the cookie. This ensures that the `maxAge` does not interfere with the cookie-clearing process.

### Testing the Change
1. **Write Tests**: After making the change, it is crucial to write tests to verify that the modification works as intended. The test should check that the `maxAge` property is ignored when clearing cookies.

2. **Run Tests**: Execute the tests to ensure that your changes do not break existing functionality and that the new behavior is correctly implemented.

## Steps to Implement the Patch

### Step 1: Modify the Function
1. Open the `lib/response.js` file.
2. Locate the `res.clearCookie` function.
3. Add the following line to delete the `maxAge` property from the options object:
    ```javascript
    delete opts.maxAge;
    ```

The modified function should look like this:
```javascript
res.clearCookie = function clearCookie(name, options) {
  var opts = merge({ expires: new Date(1), path: '/' }, options);
  delete opts.maxAge;
  
  return this.cookie(name, '', opts);
};
```

### Step 2: Write Tests
1. Open the `test/res.clearCookie.js` file.
2. Add a new test case to check that the `maxAge` property is ignored when clearing cookies:
    ```javascript
    it('should ignore maxAge', function(done){
      var app = express();

      app.use(function(req, res){
        res.clearCookie('sid', { path: '/admin', maxAge: 900 }).end();
      });

      request(app)
      .get('/')
      .expect('Set-Cookie', 'sid=; Path=/admin; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
      .expect(200, done);
    });
    ```

### Step 3: Run the Tests
1. Ensure you have the necessary dependencies installed (e.g., Mocha, Supertest).
2. Run the test suite to verify that your changes are correct:
    ```bash
    npm test
    ```

## Conclusion

By following these steps and principles, you should be able to implement patches and solve issues effectively within the codebase. Remember to always write and run tests to ensure the reliability and correctness of your changes. Welcome aboard, and happy coding!