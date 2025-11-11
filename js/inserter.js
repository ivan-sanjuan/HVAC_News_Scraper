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

function printNums(a,b){
    for (let i=a;i<=b;i++){
        if (i % 2 != 0){
            console.log(i);
        }
    }
}
printNums(1,20);

function inputName(){
    let enteredName = document.getElementById('name').value;
    let enteredAge = document.getElementById('age').value;
    document.getElementById('name_output').value =  `I am ${enteredName} and i am ${enteredAge}`;
}

var fruitArray = ['apple','orange','mango','pineapple','avocado'];

fruitArray.push('mangosteen');
console.log(fruitArray);
fruitArray.shift()
fruitArray.sort()
console.log(fruitArray)

class Car{
    constructor(brand,model,year){
        this.brand = brand;
        this.model = model;
        this.year = year;
    }
}

function printDefinition(){
    console.log(`This is a ${this.brand}, ${this.model} in the year ${this.year}`);
}

var carOne = new Car('Honda','Civic',1998);
printDefinition.call(carOne);

for (let c=1;c<=100;c++){
    if(c%3==0){
        console.log('Fizz',c);
    }
    if(c%5==0){
        console.log('Buzz',c);
    }
    if(c%3==0 && c%5==0){
        console.log('FizzBuzz',c);
    }
}

