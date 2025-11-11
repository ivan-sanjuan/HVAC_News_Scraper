'use strict';

const name = 'Ivan'
const age = 34

function declareName(){
    console.log(`My name is ${name}, i am ${age}`);
}

declareName();

var x=30;
var y=40;
function addOperation(numOne,numTwo) {
    console.log('Sum is: ', numOne+numTwo);
}

addOperation(x,y);
addOperation(100,5);

var array1 = [40,77,141,642,2132,6139]

function evenOdd(array){
    for (let num of array){
        if (num % 2 == 0){
            console.log('This is even number: ',num);
        }
        else{
            console.log('This is odd: ',num);
        }
    }
}

evenOdd(array1);

var array1 = [213,53214,5132,126,73553]

evenOdd(array1);