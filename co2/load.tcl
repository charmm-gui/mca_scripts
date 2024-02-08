mol new pet_co2_1.dcd waitfor all

set sel [atomselec top all]
$sel set radius 1.0

display resetview
display projection orthographic
pbc box

rotate x by -90

mol selection all
mol rep VDW
mol addrep top

mol selection index 38
mol rep VDW 3
mol color ColorID [colorinfo index "orange"]
mol addrep top

package require pbctools

pbc set "108.4 108.4 60"
pbc box_draw -shiftcenter {0 0 120}
pbc set "108.4 108.4 300"
