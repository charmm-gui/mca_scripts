mol new step3_assembly.psf
mol addfile openmm/step7_1000.dcd waitfor all

set cartoonmat "AOChalky"
set surfmat "AOEdgy"
set watmat "AOChalky"

# materials and colors
material add copy AOChalky
material rename Material23 AOTransparent
color Name C silver

material change opacity AOTransparent 0.15
material change ambient AOChalky 0.15
material change ambient AOEdgy 0.15
material change outline AOEdgy 3.0
material change outlinewidth AOEdgy 0.33

# keep only first frame, delete default rep
animate goto 0
animate delete beg 1 end 10 top
mol delrep top 0

# membrane
mol material AOEdgy
mol rep VDW
mol selection {(segid MEMB or segid "H.*") and not hydrogen}
mol addrep top

# KCl
mol selection {segid IONS and name POT}
mol color ColorID [colorinfo index orange]
mol addrep top

mol selection {segid IONS and not name POT}
mol color ColorID [colorinfo index purple]
mol addrep top

# proteins
mol material $cartoonmat
mol rep NewCartoon
mol selection {segid "PAA.*" and not hydrogen}
mol color ColorID [colorinfo index orange]
mol addrep top

mol material $surfmat
mol rep QuickSurf 1 .5 1 1
mol addrep top

mol material $cartoonmat
mol rep NewCartoon
mol selection {segid "PAB.*" and not hydrogen}
mol color ColorID [colorinfo index green]
mol addrep top

mol material $surfmat
mol rep QuickSurf 1 .5 1 1
mol addrep top

mol material $cartoonmat
mol rep NewCartoon
mol selection {segid "PAC.*" and not hydrogen}
mol color ColorID [colorinfo index cyan]
mol addrep top

mol material $surfmat
mol rep QuickSurf 1 .5 1 1
mol addrep top

# water
mol material $surfmat
mol rep Licorice
mol selection {water}
mol color [colorinfo index iceblue]
mol addrep top

# setup camera
rotate x by -90
#scale by 1.5
scale by 2
display projection orthographic

set outfile $image_dir/out/${system}_cartoon.$ext

if {[file exists $outfile]} {
    exec rm $outfile
}

render $renderer $outfile

if {$platform == "Darwin"} {
    exec open $outfile
}

quit
