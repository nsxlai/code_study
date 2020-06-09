# source: https://medium.com/@severinperez/maintainable-code-and-the-open-closed-principle-b088c737262
# The code from the source is using JavaScript. Will translate into Python for study purpose here.
#
# Also use the RealPython tutoral on interface to build the meta class interface
# https://realpython.com/python-interface/

import abc

class Interface(abc.ABC):
    @abc.abstractmethod
    def monster(self):
        pass

def createWithInterfaceValidation(prototypeObject, interfaceObject):



if __name__ == '__main__':
    monsters = []
    locations = ["Athens", "Budapest", "New York", "Santiago", "Tokyo"]



'''
// Interface Approximation Utilities
function ImplementationError(message) {
  this.name = "ImplementationError";
  this.message = message;
}
ImplementationError.prototype = new Error();

function createWithInterfaceValidation(prototypeObject, interfaceObject) {
  Object.keys(interfaceObject).forEach(function(key) {
    if (prototypeObject[key] === null || typeof prototypeObject[key] !== "function") {
      throw new ImplementationError(
        "Required method " + key + " has not been implemented."
      );
    }
  });

  return Object.create(prototypeObject);
}

// Monster Types and Manager
var MonsterManager = {
  init: function(monsters, locations) {
    this.monsters = monsters;
    this.locations = locations;
  },

  getRandomLocation: function() {
    function getRandomInt(max) {
      return Math.floor(Math.random() * Math.floor(max));
    }

    return this.locations[getRandomInt(this.locations.length)];
  },

  rampageAll: function() {
    this.monsters.forEach(function(monster) {
      var location = this.getRandomLocation();

      monster.rampage(location);
    }, this);
  }
};

var MonsterInterface = {
  init: null,
  rampage: null,
};

var Kaiju = Object.create(MonsterInterface);
Kaiju.init = function(name) {
  this.name = name;
  this.type = "Kaiju";

  return this;
};
Kaiju.rampage = function(location) {
  console.log(
    "The " + this.type + " " + this.name +
    " is rampaging through " + location + "!"
  );
};

var GreatOldOne = Object.create(MonsterInterface);
GreatOldOne.init = function(name) {
  this.name = name;
  this.type = "Great Old One";

  return this;
};
GreatOldOne.rampage = function(location) {
  console.log(
    "The " + this.type + " " + this.name +
    " has awaken from its slumber in " + location + "!"
  );
};

var MythicalMonster = Object.create(MonsterInterface);
MythicalMonster.init = function(name) {
  this.name = name;
  this.type = "Mythical Monster";

  return this;
};
MythicalMonster.rampage = function(location) {
  console.log(
    "The " + this.type + " " + this.name +
    " has been sighted in " + location + "!"
  );
};

// Rampage!
var monsters = [];
var locations = ["Athens", "Budapest", "New York", "Santiago", "Tokyo"];

var rodan = createWithInterfaceValidation(Kaiju, MonsterInterface);
rodan.init("Rodan");
monsters.push(rodan);

var gzxtyos = createWithInterfaceValidation(GreatOldOne, MonsterInterface);
gzxtyos.init("Gzxtyos");
monsters.push(gzxtyos);

var cerberus = createWithInterfaceValidation(MythicalMonster, MonsterInterface);
cerberus.init("Cerberus");
monsters.push(cerberus);

var myMonsterManager = Object.create(MonsterManager);
myMonsterManager.init(monsters, locations);

myMonsterManager.rampageAll();
  // Logs: (with variable city names)
    // The Kaiju Rodan is rampaging through Tokyo!
    // The Great Old One Gzxtyos has awaken from its slumber in Athens!
    // The Mythical Monster Cerberus has been sighted in New York!
'''