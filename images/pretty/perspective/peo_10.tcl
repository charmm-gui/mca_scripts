mol new step3_assembly.psf
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

# proteins
mol material AOChalky
mol rep NewCartoon
mol selection {segid "PAA.*"}
mol color ColorID [colorinfo index orange]
mol addrep top

mol selection {segid "PAB.*"}
mol color ColorID [colorinfo index green]
mol addrep top

mol selection {segid "PAC.*"}
mol color ColorID [colorinfo index cyan]
mol addrep top

# setup camera
rotate z by  25
rotate x by -65
scale by 1.4
translate by -0.15 0 0

# TODO: remove below?
material change ambient AOChalky 0.12
material change ambient AOEdgy 0.15
material change outline AOEdgy 3.0
material change outlinewidth AOEdgy 0.33

set outfile1 $image_dir/out/${system}_cartoon.tga
set outfile2 $image_dir/out/${system}_surface.tga

if {[file exists $outfile1]} {
    exec rm $outfile1
}

if {[file exists $outfile2]} {
    exec rm $outfile2
}

render TachyonInternal $outfile1
exec open $outfile1

set nr [molinfo top get numreps]
for {set i 1} {$i <= 3} {incr i} {
    set rn [expr $nr - $i]
    mol modmaterial $rn top AOEdgy
    mol modstyle $rn top QuickSurf 1 0.5 1 1
}

render TachyonInternal $outfile2
exec open $outfile2

#quit
