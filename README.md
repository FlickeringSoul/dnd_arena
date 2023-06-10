# dnd_arena
DnD 5e Battle System Implementation

---

# How to let the model be compatible with construct a tree of possibility

This tree of possibility is for both be able to construct a statistical view to compare builds
-> what's the average damage per turn on 3 turns
-> what's the likelihood of victory

But also construct a AI, making the best choices

The solution found is using a event driven system capable of stopping almost
at any stage. When there is an event (like casting a spell), every modules
(features and other) are called using this event, one by one, event stage by event stage.

So if a module has a choice, random outcome or trigger another event, it can interrupt
saving the all state and split in two (or more)

---

---

# How to remove a temporary action when it's effect ends ?

Main case: eldritch blast allow several blast, which is view as a temporary possible action with cost=None

The effect can takes several turns like spider legs.
The effect may end due to dispel

Same question for temporary features like Poisoning -> may end in 2 turns or on healing

-> adding a boolean attribute `to_delete` that is checked at the end of every steps ?

Actions & Features needs tags like `Healable`, `Magical` and so on, to be properly affected by anti-magic or heals

But how to trigger something on end of turn or else ? how to update `to_delete`

-> features and action should both be subscribed to events

how to call them ? skills -> being poison is not a skill, it's rather a status. EldritchBlast is not a status.
EventListener ?

=> Solution

Use modules. A module is something. Spider's poison, Eldritch Blast, Inspiration Dice... whatever.
This module is subscribed to every events: End of Turn, Dispel event, an attack, choosing action...
And it act it. Either ignoring it, changing it's internal state, responding to it by responding that a
choice must be made, responding to it with random outcomes, or modifying it like with `choosing action event` and
saying an action is available

Action, Passive Features, Reaction Sills or Spells, Temporary Effects, Permanent Effects they are all modules.

Modules have a `to_delete` boolean attribute to say when they must be destroyed

Modules should not be linked to characters since terrain effect can exist too.

---

# How to counterspell a counterspell ?

---

# How to select a target ?

-> Select a cell to go, a monster to attack ?

Tree of Possibility must reflect all available choices, how to know available choices ?

Targets are only Characters ? What if we want to target a spaces like with AoE or Bonefire ?
what about targeting a specific poison on heal ?

What about feature making you invisible ?

State must have a function to list all available targets depending on input parameters
Module proposing actions must call that function fist and let a possibility for each available
targets.

Actually, choosing action event must propose this function

this event should also hold the action, action bonus, interaction, spell slots of the character choosing it's action

---

# How to construct a tree of possibilities with dices with ressistences ?

Resist halves damages, taking two times 3 dmg is a total of 2 whearas taking one time six, result in three
how to construct this ?

-> seperate dices rools ?

---

# How to deal with negative dices

A protection that reduce damage taken by 1d8 cannot go beyond initial damage
how to take this into account

---

# How to deal with opportunity attacks ? Worse, WarMage cantrip

---

# How to deal with knowledge that AI should not use ?

AI should not know in advance resistances, HP, enemies abilities and so on
How to take it into account ?

-> enemy model should be evolutive depending on what we saw
before knowing, it could be either default value of probability
-> fire res probability = 10%
-> invisible character has equal probabilities of being where it can ? that's not true but how to predict ?
-> going invisible somewhere may be strategic -> using invisibility mean anticipating how ennemies will react to it

---

# How to compute average DPR of a build ?

According to (rpg.stackexchange)[https://rpg.stackexchange.com/questions/200182/is-there-any-estimate-of-average-damage-output-per-turn-for-pcs-by-level]
a fight is around 4 rounds, so we could take the avg in 4 rounds

---

# How to compare builds ?

There is the avg DPT dealt, DPT received but also their variance.
A polyvalent build can deal with more monster variety

But what about team work ? Blessing spell is strong but not alone
Bonuses to other should not be overlooked
