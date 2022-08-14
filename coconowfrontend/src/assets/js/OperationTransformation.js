

export var isRetain = function(op){
  return typeof op === 'number' && op > 0;
}

export var isInsert = function (op) {
  return typeof op === 'string';
};

export var isDelete = function (op) {
  return typeof op === 'number' && op < 0;
};

export class Operation{
  constructor(){
    this.ops=[]
    this.baseLength=0
    this.targetLength=0
  }  
  retain(n){
    if (typeof n !== 'number') {
      throw new Error("retain expects an integer");
    }
    if (n === 0) { return this; }
    this.baseLength += n;
    this.targetLength += n;
    if (isRetain(this.ops[this.ops.length-1])) {
      this.ops[this.ops.length-1] += n;
    } else {
      this.ops.push(n);
    }
    return this;
  }
  insert(str){
    if (typeof str !== 'string') {
      throw new Error("insert expects a string");
    }
    if (str === '') { return this; }
    this.targetLength += str.length;
    var ops = this.ops;
    if (isInsert(ops[ops.length-1])) {
      ops[ops.length-1] += str;
    } else if (isDelete(ops[ops.length-1])) {
      if (isInsert(ops[ops.length-2])) {
        ops[ops.length-2] += str;
      } else {
        ops[ops.length] = ops[ops.length-1];
        ops[ops.length-2] = str;
      }
    } else {
      ops.push(str);
    }
    return this;
  }
  delete(n){
    if (typeof n === 'string') { n = n.length; }
    if (typeof n !== 'number') {
      throw new Error("delete expects an integer or a string");
    }
    if (n === 0) { return this; }
    if (n > 0) { n = -n; }
    this.baseLength -= n;
    if (isDelete(this.ops[this.ops.length-1])) {
      this.ops[this.ops.length-1] += n;
    } else {
      this.ops.push(n);
    }
    return this;
  }
  isNoop(){
    return this.ops.length === 0 || (this.ops.length === 1 && isRetain(this.ops[0]));
  }
  toString(){
    var map = Array.prototype.map || function (fn) {
      var arr = this;
      var newArr = [];
      for (var i = 0, l = arr.length; i < l; i++) {
        newArr[i] = fn(arr[i]);
      }
      return newArr;
    };
    return map.call(this.ops, function (op) {
      if (isRetain(op)) {
        return "retain " + op;
      } else if (isInsert(op)) {
        return "insert '" + op + "'";
      } else {
        return "delete " + (-op);
      }
    }).join(', ');
  }
  toJSON(){
    return this.ops;
  }
  fromJSON(ops){
    var o = new Operation();
    for (var i = 0, l = ops.length; i < l; i++) {
      var op = ops[i];
      if (isRetain(op)) {
        o.retain(op);
      } else if (isInsert(op)) {
        o.insert(op);
      } else if (isDelete(op)) {
        o.delete(op);
      } else {
        throw new Error("unknown operation: " + JSON.stringify(op));
      }
    }
    return o;
  }
  apply(str){
    var operation = this;
    if (str.length !== operation.baseLength) {
      throw new Error("The operation's base length must be equal to the string's length.");
    }
    var newStr = [], j = 0;
    var strIndex = 0;
    var ops = this.ops;
    for (var i = 0, l = ops.length; i < l; i++) {
      var op = ops[i];
      if (isRetain(op)) {
        if (strIndex + op > str.length) {
          throw new Error("Operation can't retain more characters than are left in the string.");
        }
        newStr[j++] = str.slice(strIndex, strIndex + op);
        strIndex += op;
      } else if (isInsert(op)) {
        newStr[j++] = op;
      } else { // delete op
        strIndex -= op;
      }
    }
    if (strIndex !== str.length) {
      throw new Error("The operation didn't operate on the whole string.");
    }
    return newStr.join('');
  }
  compose(operation2){
    var operation1 = this;
    if (operation1.targetLength !== operation2.baseLength) {
      throw new Error("The base length of the second operation has to be the target length of the first operation");
    }

    var operation = new Operation(); // the combined operation
    var ops1 = operation1.ops, ops2 = operation2.ops; // for fast access
    var i1 = 0, i2 = 0; // current index into ops1 respectively ops2
    var op1 = ops1[i1++], op2 = ops2[i2++]; // current ops
    while (true) {
      if (typeof op1 === 'undefined' && typeof op2 === 'undefined') {
        break;
      }

      if (isDelete(op1)) {
        operation['delete'](op1);
        op1 = ops1[i1++];
        continue;
      }
      if (isInsert(op2)) {
        operation.insert(op2);
        op2 = ops2[i2++];
        continue;
      }

      if (typeof op1 === 'undefined') {
        throw new Error("Cannot compose operations: first operation is too short.");
      }
      if (typeof op2 === 'undefined') {
        throw new Error("Cannot compose operations: first operation is too long.");
      }

      if (isRetain(op1) && isRetain(op2)) {
        if (op1 > op2) {
          operation.retain(op2);
          op1 = op1 - op2;
          op2 = ops2[i2++];
        } else if (op1 === op2) {
          operation.retain(op1);
          op1 = ops1[i1++];
          op2 = ops2[i2++];
        } else {
          operation.retain(op1);
          op2 = op2 - op1;
          op1 = ops1[i1++];
        }
      } else if (isInsert(op1) && isDelete(op2)) {
        if (op1.length > -op2) {
          op1 = op1.slice(-op2);
          op2 = ops2[i2++];
        } else if (op1.length === -op2) {
          op1 = ops1[i1++];
          op2 = ops2[i2++];
        } else {
          op2 = op2 + op1.length;
          op1 = ops1[i1++];
        }
      } else if (isInsert(op1) && isRetain(op2)) {
        if (op1.length > op2) {
          operation.insert(op1.slice(0, op2));
          op1 = op1.slice(op2);
          op2 = ops2[i2++];
        } else if (op1.length === op2) {
          operation.insert(op1);
          op1 = ops1[i1++];
          op2 = ops2[i2++];
        } else {
          operation.insert(op1);
          op2 = op2 - op1.length;
          op1 = ops1[i1++];
        }
      } else if (isRetain(op1) && isDelete(op2)) {
        if (op1 > -op2) {
          operation['delete'](op2);
          op1 = op1 + op2;
          op2 = ops2[i2++];
        } else if (op1 === -op2) {
          operation['delete'](op2);
          op1 = ops1[i1++];
          op2 = ops2[i2++];
        } else {
          operation['delete'](op1);
          op2 = op2 + op1;
          op1 = ops1[i1++];
        }
      } else {
        throw new Error(
          "This shouldn't happen: op1: " +
          JSON.stringify(op1) + ", op2: " +
          JSON.stringify(op2)
        );
      }
    }
    return operation;
  }
  getSimpleOp(){
    var ops = this.ops;
    switch (ops.length) {
      case 1:
        return ops[0];
      case 2:
        return isRetain(ops[0]) ? ops[1] : (isRetain(ops[1]) ? ops[0] : null);
      case 3:
        if (isRetain(ops[0]) && isRetain(ops[2])) { return ops[1]; }
      }
      return null;
  }
  getStartIndex(){
    if (isRetain(this.ops[0])) { return this.ops[0]; }
    return 0;
  }
  
}

export var transform = function(operation1, operation2){
  if (operation1.baseLength !== operation2.baseLength) {
    throw new Error("Both operations have to have the same base length");
  }

  var operation1prime = new Operation();
  var operation2prime = new Operation();
  var ops1 = operation1.ops, ops2 = operation2.ops;
  var i1 = 0, i2 = 0;
  var op1 = ops1[i1++], op2 = ops2[i2++];
  while (true) {

    if (typeof op1 === 'undefined' && typeof op2 === 'undefined') {
      break;
    }


    if (isInsert(op1)) {
      operation1prime.insert(op1);
      operation2prime.retain(op1.length);
      op1 = ops1[i1++];
      continue;
    }
    if (isInsert(op2)) {
      operation1prime.retain(op2.length);
      operation2prime.insert(op2);
      op2 = ops2[i2++];
      continue;
    }

    if (typeof op1 === 'undefined') {
      throw new Error("Cannot compose operations: first operation is too short.");
    }
    if (typeof op2 === 'undefined') {
      throw new Error("Cannot compose operations: first operation is too long.");
    }

    var minl;
    if (isRetain(op1) && isRetain(op2)) {
      if (op1 > op2) {
        minl = op2;
        op1 = op1 - op2;
        op2 = ops2[i2++];
      } else if (op1 === op2) {
        minl = op2;
        op1 = ops1[i1++];
        op2 = ops2[i2++];
      } else {
        minl = op1;
        op2 = op2 - op1;
        op1 = ops1[i1++];
      }
      operation1prime.retain(minl);
      operation2prime.retain(minl);
    } else if (isDelete(op1) && isDelete(op2)) {
      if (-op1 > -op2) {
        op1 = op1 - op2;
        op2 = ops2[i2++];
      } else if (op1 === op2) {
        op1 = ops1[i1++];
        op2 = ops2[i2++];
      } else {
        op2 = op2 - op1;
        op1 = ops1[i1++];
      }
    } else if (isDelete(op1) && isRetain(op2)) {
      if (-op1 > op2) {
        minl = op2;
        op1 = op1 + op2;
        op2 = ops2[i2++];
      } else if (-op1 === op2) {
        minl = op2;
        op1 = ops1[i1++];
        op2 = ops2[i2++];
      } else {
        minl = -op1;
        op2 = op2 + op1;
        op1 = ops1[i1++];
      }
      operation1prime['delete'](minl);
    } else if (isRetain(op1) && isDelete(op2)) {
      if (op1 > -op2) {
        minl = -op2;
        op1 = op1 + op2;
        op2 = ops2[i2++];
      } else if (op1 === -op2) {
        minl = op1;
        op1 = ops1[i1++];
        op2 = ops2[i2++];
      } else {
        minl = op1;
        op2 = op2 + op1;
        op1 = ops1[i1++];
      }
      operation2prime['delete'](minl);
    } else {
      throw new Error("The two operations aren't compatible");
    }
  }

  return [operation1prime, operation2prime];
}

export var OperationFromJSON = function(ops){
  var o = new Operation();
  for (var i = 0, l = ops.length; i < l; i++) {
    var op = ops[i];
    if (isRetain(op)) {
      o.retain(op);
    } else if (isInsert(op)) {
      o.insert(op);
    } else if (isDelete(op)) {
      o.delete(op);
    } else {
      throw new Error("unknown operation: " + JSON.stringify(op));
    }
  }
  return o;
}


function opEqual(operation1,operation2){
  if(operation1.baseLength !== operation2.baseLength){
    return false;
  }
  if(operation1.targetLength !== operation2.targetLength){
    return false;
  }
  if(operation1.ops.length !== operation2.ops.length){
    return false;
  }
  for(var i=0; i<operation1.ops.length;i++){
    if(operation1.ops[i]!==operation2.ops[i]){
      return false
    }
  }
  return true;
}

export let Client = (function (global) {
  'use strict';

  function Client () {
    this.revision = 0; // the next expected revision number
    this.state = synchronized_; // start state
  }

  Client.prototype.setState = function (state) {
    this.state = state;
  };

  Client.prototype.applyClient = function (operation) {
    this.setState(this.state.applyClient(this, operation));
  };

  Client.prototype.applyServer = function (operation) {
    this.revision++;
    this.setState(this.state.applyServer(this, operation));
  };

  Client.prototype.serverAck = function () {
    this.revision++;
    this.setState(this.state.serverAck(this));
  };
  
  Client.prototype.serverReconnect = function () {
    if (typeof this.state.resend === 'function') { this.state.resend(this); }
  };

  Client.prototype.transformSelection = function (selection) {
    return this.state.transformSelection(selection);
  };

  Client.prototype.sendOperation = function (revision, operation) {
    throw new Error("sendOperation must be defined in child class");
  };

  Client.prototype.applyOperation = function (operation) {
    throw new Error("applyOperation must be defined in child class");
  };

  Client.prototype.resend = function(){
    this.state.resend(this);
  }


  function Synchronized () {}
  Client.Synchronized = Synchronized;

  Synchronized.prototype.applyClient = function (client, operation) {
    client.sendOperation(client.revision, operation);
    return new AwaitingConfirm(operation);
  };

  Synchronized.prototype.applyServer = function (client, operation) {
    client.applyOperation(operation);
    return this;
  };

  Synchronized.prototype.serverAck = function (client) {
    throw new Error("There is no pending operation.");
  };

  Synchronized.prototype.transformSelection = function (x) { return x; };

  var synchronized_ = new Synchronized();


  function AwaitingConfirm (outstanding) {
    // Save the pending operation
    this.outstanding = outstanding;
  }
  Client.AwaitingConfirm = AwaitingConfirm;

  AwaitingConfirm.prototype.applyClient = function (client, operation) {
    return new AwaitingWithBuffer(this.outstanding, operation);
  };

  AwaitingConfirm.prototype.applyServer = function (client, operation) {
    var pair = transform(this.outstanding, operation);
    client.applyOperation(pair[1]);
    return new AwaitingConfirm(pair[0]);
  };

  AwaitingConfirm.prototype.serverAck = function (client) {
    return synchronized_;
  };

  AwaitingConfirm.prototype.transformSelection = function (selection) {
    return selection.transform(this.outstanding);
  };

  AwaitingConfirm.prototype.resend = function (client) {
    client.sendOperation(client.revision, this.outstanding);
  };


  function AwaitingWithBuffer (outstanding, buffer) {
    this.outstanding = outstanding;
    this.buffer = buffer;
  }
  Client.AwaitingWithBuffer = AwaitingWithBuffer;

  AwaitingWithBuffer.prototype.applyClient = function (client, operation) {
    var newBuffer = this.buffer.compose(operation);
    return new AwaitingWithBuffer(this.outstanding, newBuffer);
  };

  AwaitingWithBuffer.prototype.applyServer = function (client, operation) {
    var pair1 = transform(this.outstanding, operation);
    var pair2 = transform(this.buffer, pair1[1]);
    client.applyOperation(pair2[1]);
    return new AwaitingWithBuffer(pair1[0], pair2[0]);
  };

  AwaitingWithBuffer.prototype.serverAck = function (client) {
    client.sendOperation(client.revision, this.buffer);
    return new AwaitingConfirm(this.buffer);
  };

  AwaitingWithBuffer.prototype.transformSelection = function (selection) {
    return selection.transform(this.outstanding).transform(this.buffer);
  };

  AwaitingWithBuffer.prototype.resend = function (client) {
    client.sendOperation(client.revision, this.outstanding);
  };


  return Client;

}(this));

