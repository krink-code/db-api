
# db-api.js

JavaScript guidelines  
https://developer.mozilla.org/en-US/docs/MDN/Guidelines/Code_guidelines/JavaScript  

```
<script src="https://cdn/db-api.min.js"
        integrity="sha256-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        crossorigin="anonymous"></script>
```

# db-api.min.js
minify db-api js file; remove comments and all white space  


---  

https://developer.mozilla.org/en-US/docs/MDN/About   
https://developer.mozilla.org/en-US/docs/Web/Guide    

https://www.w3.org/TR/SRI/   

https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Client-side_JavaScript_frameworks    
https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Client-side_JavaScript_frameworks/Introduction    

---    

Package Management    
https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Understanding_client-side_tools/Package_management    

https://docs.npmjs.com/creating-a-package-json-file    

package.json    

https://www.npmjs.com/    
https://nodejs.org/en/knowledge/getting-started/npm/what-is-npm/       


Node.js includes npm (the node package manager), and npx (the node package runner).



---
React app    
https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Client-side_JavaScript_frameworks/React_getting_started


---

# JavaScript modules

In the beginning, Javascript did not have a way to import/export modules.  
ECMAScript modules are the official standard format to package JavaScript code.  
https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules  

### CJS is short for CommonJS
```
//importing 
const doSomething = require('./doSomething.js'); 

//exporting
module.exports = function doSomething(n) {
  // do something
}
```
const myLocalModule = require('./some/local/file.js') or var React = require('react'); 

node.js traditionally used CJS module format, but now supports ECMAScript modules

backend (server side) transpiled and bundled


### AMD stands for Asynchronous Module Definition
```
define(['dep1', 'dep2'], function (dep1, dep2) {
    //Define the module value by returning a value.
    return function () {};
});

```
"simplified CommonJS wrapping" https://requirejs.org/docs/whyamd.html
```
define(function (require) {
    var dep1 = require('dep1'),
        dep2 = require('dep2');
    return function () {};
});
```

frontend (browser side)


### UMD stands for Universal Module Definition  
https://github.com/umdjs/umd/  
```
(function (root, factory) {
    if (typeof define === "function" && define.amd) {
        define(["jquery", "underscore"], factory);
    } else if (typeof exports === "object") {
        module.exports = factory(require("jquery"), require("underscore"));
    } else {
        root.Requester = factory(root.$, root._);
    }
}(this, function ($, _) {
    // define module implementation here...

    var Requester = { // ... };

    return Requester;
}));
```

bundler format for Rollup, Webpack

backend+frontend (serverside/browserside)


### ESM stands for ES Modules (ECMAScript Modules)
Javascript proposal to implement a standard module system ECMAScript
https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules
```
import React from 'react';
```
```
import {foo, bar} from './myLib';

...

export default function() {
  // your Function
};
export const function1() {...};
export const function2() {...};
```

works with "modern" browsers only,
```
<script type="module">
  import {func1} from 'my-lib';

  func1();
</script>
```

ECMAScript specification 
https://tc39.es/ecma262/

node.js newer versions support ECMAScript modules  
https://nodejs.org/dist/latest-v13.x/docs/api/esm.html#esm_ecmascript_modules




