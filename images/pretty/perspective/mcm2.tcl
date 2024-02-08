mol new step5_assembly.psf
mol addfile openmm/step7_1000.dcd waitfor all

# keep only first frame, delete default rep
animate goto 0
animate delete beg 1 end 10 top
mol delrep top 0

# membrane
mol material AOEdgy
mol rep VDW
mol selection {segid MEMB or segid "H.*"}
mol addrep top

# KCl
mol selection {segid IONS and name POT}
mol color ColorID [colorinfo index orange]
mol addrep top

mol selection {segid IONS and not name POT}
mol color ColorID [colorinfo index purple]
mol addrep top

package require pbctools
pbc wrap -orthorhombic -shiftcenterrel {0 0 0.2}
pbc join fragment -sel {segid MEMB}

# setup camera
display resetview
rotate z by -25
rotate x by  95
scale by 1.25
translate by -0.15 0.0 0.0

# TODO: remove below?
material change ambient AOEdgy 0.12
material change outline AOEdgy 3.0
material change outlinewidth AOEdgy 0.33

set outfile $image_dir/out/${system}.tga

if {[file exists $outfile]} {
    exec rm $outfile
}

render TachyonInternal $outfile
exec open $outfile

quit
