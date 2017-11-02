Tangos Tutorial – Gadget+SubFind
================================

Import the simulation
---------------------

At the unix command line type:

```
tangos_manager add tutorial_gadget --min-particles 100
```

The process should take about a minute on a standard modern computer, during which you'll see a bunch of log messages 
scroll up the screen.
 
 Let's pick this command apart
 
  * `tangos_manager` is the command-line tool to administrate your tangos database
  * `add` is a subcommand to add a new simulation
  * `tutorial_gadget` identifies the simulation we're adding
  * `--handler pynbody.GadgetSubfindOutputSetHandler` identifies the _handler_ for our simulation. A handler defines how to load a simulation and its associated halo catalogue. Here we'll use `pynbody`'s ability to load gadget and subfind files. 
  * `--min-particles 100` imports only halos/groups with at least 100 particles. 
  (The default value is 1000 particles, but this tutorial dataset is fairly low resolution so we'll keep these small halos.)

 
Note that all _tangos_ command-line tools provide help. For example `tangos_manager --help` will show you all subcommands, and `tangos_manager add --help` will tell you more about the possible options for adding a simulation.
  
At this point, the database knows about the existence of timesteps and their halos and groups in our simulation, but nothing about the properties of those halos or groups. We need to add more information before the database is useful.


Import subfind's properties
---------------------------

At the unix command line type:

```
tangos_import_from_subfind --sims tutorial_gadget
```

The process should take about a minute on a standard modern computer, during which you'll see a bunch of log messages scroll up the screen.

Note that if you did not correctly specify the Subfind handler in the step above, this will just generate an error. To recover from that situation, the easiest thing is to delete the database file you created and start again.

Generate the merger trees
-------------------------

The merger trees are most simply generated using pynbody's bridge function to do this, type

```
tangos_timelink --sims tutorial_gadget
```

which builds the merger tree for the halos, and then you probably also want to run

```
tangos_timelink --type group --sims tutorial_gadget
```
to make the merger tree for the groups. If you want to speed up these processes, they can each be 
[MPI parallelised](mpi.md).

The construction of each merger tree should take a couple of minutes,  and again you'll see a log scroll up the screen while it happens.


Add some more interesting properties
------------------------------------

Let's finally do some science. We'll add dark matter density profiles; from your shell type:
 
 ```bash
tangos_writer dm_density_profile --with-prerequisites --include-only="NDM()>5000" --type=halo --sims tutorial_gadget
```

If you want to speed up this process, it can be [MPI parallelised](mpi.md).

Here,
 * `tangos_writer` is the same script you called above to add properties to the database
 * `dm_density_profile` is an array representing the dark matter density profile; to see all available properties
   you can call `tangos_manager list-possible-haloproperties`
 * `--with-prerequisites` automatically includes  any underlying properties that are required to perform the calculation. In this case,
   the `dm_density_profile` calculation actually needs to know an accurate center for the halo (known as `shrink_center`),
   so that calculation will be automatically performed and stored
 * `--include-only` allows an arbitrary filter to be applied, specifying which halos the properties should be calculated
   for. In the present case, we use that to insist that only halos with more than 5000 particles have their density profiles
   calculated
 * `--type=halo` calculates the properties only for halos (as opposed to groups)
 
 
Now let's take a look at what we've created
-------------------------------------------

We're ready to explore the simulation. Depending on your preferences you might prefer to explore with the web service or direct from python. 