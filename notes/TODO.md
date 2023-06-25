
# Builds

* Implement halfling rogue to have a basic build comparison
* Implement summon undead (skeleton) -> group -> better vision for the genie build
* Implement pact of the chain -> familiar conditional attack
* Take into account darkness strategy for low level warlock
* Implement zeolot barbarian
* Implement Battle Smith Artificier
* Implement Wildfire Druid

# Transversal improvement

* Have a way to properly see bonus AR of support action with teamplay -> bless spell, Artficier magic weapon given to other...
* Create a better workbanch with real monsters:
* * See how damage type affect avg damage (dealt and received)
* * Compute percentage of maxlife dealt -> much better than raw damage
* * Cap max damage of a single hit at 150% of max life to favorize robust play style

# Tree search improvements

* Compute avrg on 4 first turns
* Regroup same states in one

# AI

* Value potential mistake from adversary
* Act on unknown -> learner, potential resistances, ...
* * Allow each character to have a model for adversary

# Quality

* Tests on simple cases

# End goal

* Implement space & movement:
* * Detect reachable, halfcover and all
* Create a Visual Interface to move and select characters/actions
* Create two ends points -> One DM UI and one player UI