'use strict';
var BigNumber = require('bignumber.js');

module.exports.hello = (event, context, callback) => {
  var a = event.number;
  var result = new BigNumber(fibonacci(a));
  console.log('after fib call..')
  const response = {
      output: result.toString(),
      input: event.number
  };

  callback(null, response);

  // Use this code if you don't use the http event with the LAMBDA-PROXY integration
  // callback(null, { message: 'Go Serverless v1.0! Your function executed successfully!', event });
};
function fibonacci(num){

  var a = new BigNumber(1);         // "11"
  var b = new BigNumber(0);
  var temp = a;

  while (num >= 0){
    temp = a;
    a = a.plus(b);
    b = temp;
    num--;
  }

  return b;
}